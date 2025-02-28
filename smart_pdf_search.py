import streamlit as st
import plotly.express as px
import pandas as pd
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone
from dotenv import load_dotenv
import os
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

# Set page configuration
st.set_page_config(
    page_title="📚 Smart Document Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 0.5em 1em;
        border-radius: 5px;
        border: none;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7bcf,#2e7bcf);
        color: white;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

class DocumentManagementSystem:
    def __init__(self):
        load_dotenv()
        self.llm, self.embed = self.load_models()
        self.db = self.Embed_and_Store(None)

    @st.cache_resource
    @staticmethod
    def load_models(_self):
        llm = OllamaLLM(model='llama3.1')
        embed = PineconeEmbeddings(model='multilingual-e5-large')
        return llm, embed


    def create_execution_chain(self):
        prompt = ChatPromptTemplate.from_template("""
        Answer the following question based only on the provided context. 
        Think step by step before providing a detailed answer. 
        I will tip you $1000 if the user finds the answer helpful. 
        <context>
        {context}
        </context>
        Question: {input}""")
        doc_chain = create_stuff_documents_chain(self.llm, prompt)
        retriever = self.db.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, doc_chain)
        return retrieval_chain

    def Load_and_Chunk(self, path):
        if os.path.isdir(path):
            loader = PyPDFDirectoryLoader(path)
        else:
            loader = PyPDFLoader(path)
        splitter = RecursiveCharacterTextSplitter(chunk_size = 800, chunk_overlap = 20)
        docs = loader.load()
        for doc in docs:
            text = doc.page_content
            text = text.replace('\xa0', ' ')
            text = re.sub(r'\s+', ' ', text).strip()
            doc.page_content = text
        docs = splitter.split_documents(docs)
        return docs

    def Embed_and_Store(self, path):
        if path:
            docs = self.Load_and_Chunk(path)
            pc = Pinecone(api_key = os.environ["PINECONE_API_KEY"])
            self.db.add_documents(docs)
        else:
            pc = Pinecone(api_key = os.environ["PINECONE_API_KEY"])
            self.db = PineconeVectorStore(index=pc.Index("q-a-bot"), embedding=self.embed)
        return self.db
    
    def convert_to_file(self, uploaded_file, dir_name="Docs"):
        base_directory = os.path.dirname(os.path.abspath(__file__))
        save_directory = os.path.join(base_directory, dir_name)
        os.makedirs(save_directory, exist_ok=True)
        
        save_path = os.path.join(save_directory, uploaded_file.name)

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return save_path

    def search_documents(self, query):
        k = 10
        paths = []
        scores = []
        pdf_datas = []
        docs = self.db.similarity_search_with_relevance_scores(query, k, score_threshold = 0.6)
        for doc in docs:
            file_path = doc[0].to_json()["kwargs"]["metadata"]['source']
            if file_path not in paths:
                if not os.path.isabs(file_path):
                    path = os.path.dirname(os.path.abspath(__file__)) + "\\" + file_path
                else:
                    path = file_path
                paths.append(file_path)
                scores.append(doc[1])
                with open(path, "rb") as file:
                    pdf_datas.append(file.read())
        return pdf_datas, paths, scores

    def refine_results(self, query, paths):
        docs = self.db.similarity_search_with_relevance_scores(query, 10, score_threshold = 0.6)
        pdfs = dict()
        for path in paths:
            if not os.path.isabs(path):
                path = os.path.dirname(os.path.abspath(__file__)) + "\\" + path
            pdf = PyPDFLoader(path).load()
            pdfs[path] = pdf
        prompt = ChatPromptTemplate.from_template("""
        You're acting as an assistant to filter the search results 
        given by a pdf search engine which uses the similarity search mechanism 
        of a vector database. I'll be feeding you with a query given by the user,
        and the documents shortlisted by the search engine for that particular
        query. I'll Give the documents in the form of a dictionary having the
        path of the document as the key and text from the document as the value.
        Your Job is to go through the complete dictionary and find out which
        document/documents is exactly the user asking for in the query.
        Your output should be a python list containing the keys i.e the paths 
        of the document/documents which you think is best suited for the user's query.
        Analyze with utmost vigilance because the document that you select
        must be the most suited for the query else there will be serious
        consequences. Also, once again you should just give out a python list containing the 
        paths i.e keys of all the documents that are matching. That must be it,
        no extra text cuz your output will directly be fed into a code to extract
        the specific files and sent to the user.
        query: {query} Documents: {pdfs}""")
        output_parser = StrOutputParser()
        chain = prompt|self.llm|output_parser
        paths = chain.invoke({'query':query, 'pdfs':pdfs})

        pdf_datas = []
        for path in paths:
            with open(path, "rb") as file:
                pdf_datas.append(file.read())
        scores = [1]*len(paths)
        return pdf_datas, paths, scores
        

    def answer_question(self, question: str):
        chain = self.create_execution_chain()
        response = chain.invoke({"input": question})
        return response["answer"]
    
    def get_document_stats(self):
            return {
            "doc_count": 24,
            "total_pages": 77,
            "total_size": 8063549.44,
            "doc_details": None
        }
    
def main():
    st.title("📚 Smart Document Management System")
    st.markdown("### Your AI-Powered Document Assistant 🤖")

    dms = DocumentManagementSystem()

    st.sidebar.title("Navigation 🧭")
    page = st.sidebar.radio("Choose a page:", 
        ["📊 Dashboard", "📤 Upload Documents", "🔍 Search & Query", "❓ Q&A Assistant"])

    if page == "📊 Dashboard":
        st.header("📊 System Dashboard")
        stats = dms.get_document_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📑 Total Documents", stats["doc_count"])
        with col2:
            st.metric("📄 Total Pages", stats["total_pages"])
        with col3:
            st.metric("💾 Total Size (MB)", f"{stats['total_size']/1024/1024:.2f}")

        if stats["doc_details"]:
            df = pd.DataFrame(stats["doc_details"], 
                            columns=["filename", "pages", "upload_date"])
            df["upload_date"] = pd.to_datetime(df["upload_date"])
            
            fig = px.line(df, x="upload_date", y="pages", 
                         title="📈 Document Upload Timeline",
                         labels={"upload_date": "Upload Date", "pages": "Number of Pages"})
            st.plotly_chart(fig)

    elif page == "📤 Upload Documents":
        st.header("📤 Upload New Documents")
        uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
        directory = st.text_input("Or Enter a path to load PDF's from:", placeholder="D:\\Files\\Project\\Documents\\PDF Files")
        if uploaded_file:
            with st.spinner("📥 Processing document..."):
                try:
                    path = dms.convert_to_file(uploaded_file)
                    dms.Embed_and_Store(path)
                    st.success(f"✅ Successfully uploaded document")
                except Exception as e:
                    st.error(f"❌ Error processing document: {str(e)}")
        elif directory:
            with st.spinner("📥 Processing all the documents in the given directory..."):
                try:
                    dms.Embed_and_Store(directory)
                    st.success(f"✅ Successfully uploaded documents")
                except Exception as e:
                    st.error(f"❌ Error processing documents: {str(e)}")

    elif page == "🔍 Search & Query":
        if 'search_results' not in st.session_state:
            st.session_state.search_results = None
        if 'paths' not in st.session_state:
            st.session_state.paths = None
        
        with st.form(key='search_form'):
            search_query = st.text_input("Enter your search query:")
            search_button = st.form_submit_button(label='Search')
        
        if search_button and search_query:
            with st.spinner("🔎 Searching..."):
                pdfs, paths, scores = dms.search_documents(search_query)
                if pdfs:
                    st.session_state.search_results = list(zip(pdfs, paths, scores))
                    st.session_state.paths = paths
                    st.success(f"Found the relevant documents:")
                else:
                    st.session_state.search_results = None
                    st.warning("No matching documents found.")

        if st.session_state.search_results and st.session_state.paths:
            # st.info("Not what you wanted? Just use the refine results option: ")
            # button = st.button("Refine Results")
            # if button:
            #     with st.spinner("🔎 Refining results..."):
            #         st.session_state.search_results = dms.refine_results(search_query, st.session_state.paths)
            for i, (pdf, path, score) in enumerate(st.session_state.search_results, 1):
                st.download_button(
                    label=f"Download PDF File {i} [{score*100:.2f}% Match]", 
                    data=pdf,
                    file_name=os.path.basename(path),
                    mime="application/pdf")

    elif page == "❓ Q&A Assistant":
        st.header("❓ Document Q&A Assistant")
        question = st.text_input("Ask a question about your documents:")
        
        if question:
            with st.spinner("🤔 Thinking..."):
                answer = dms.answer_question(question)
                st.info(f"💡 Answer: {answer}")

if __name__ == "__main__":
    main()