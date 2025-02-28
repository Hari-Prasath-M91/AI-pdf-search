# Smart Document Management System and Search Engine

## Overview
This is a **Streamlit-based** Smart Document Management System that allows users to upload, search, and query PDF documents using **LangChain, Pinecone, and Ollama LLM**. The system enables similarity-based document retrieval and Q&A functionalities.

## Features
- **Upload PDF documents** 📤
- **Search and retrieve documents using Pinecone** 🔍
- **AI-powered Q&A Assistant** ❓
- **Interactive dashboard with analytics** 📊
  
## 📖 Index
1. [Installation & Setup](#installation--setup)
    - [Clone the Repository](#1-clone-the-repository)
    - [Set Up Virtual Environment](#2-set-up-virtual-environment-optional-but-recommended)
    - [Install Dependencies](#3-install-dependencies)
    - [Set Up Environment Variables](#4-set-up-environment-variables)
    - [Creating Accounts & API Keys](#creating-accounts--api-keys)
    - [Run the Application](#5-run-the-application)
2. [Usage](#usage)
    - [Dashboard](#-dashboard)
    - [Upload Documents](#-upload-documents)
    - [Search & Query](#-search--query)
    - [Q&A Assistant](#-qa-assistant)
3. [Troubleshooting](#troubleshooting)
4. [License](#license)
5. [Contact](#contact)


## Installation & Setup

### **1. Clone the Repository**
```sh
git clone https://github.com/your-repository-url.git
cd your-repository-folder
```

### **2. Set Up Virtual Environment (Optional but Recommended)**
```sh
python -m venv venv
source venv/bin/activate  # On Mac/Linux
venv\Scripts\activate    # On Windows
```

### **3. Install Dependencies**
```sh
pip install -r requirements.txt
```

### **4. Set Up Environment Variables**
A `.env.example` file is provided in the repository. Copy and rename it to `.env`, then modify the values accordingly:
```sh
cp .env.example .env  # For Mac/Linux
copy .env.example .env  # For Windows (CMD)
```
Then, edit the `.env` file to include your API keys.

#### **Creating Accounts & API Keys**

**LangChain:**
1. Visit [LangChain](https://www.langchain.com/).
2. Sign up and generate an API key.
3. Add it to your `.env` file.

**Pinecone:**
1. Visit [Pinecone](https://www.pinecone.io/).
2. Sign up and create an account.
3. Navigate to **API Keys** and generate a key.
4. Add the API key to your `.env` file:
   ```
   PINECONE_API_KEY=your_pinecone_api_key
   ```

### **5. Run the Application**
```sh
streamlit run smart_pdf_search.py
```

## Usage

### **📊 Dashboard**
- View system statistics, including total documents, pages, and size.

### **📤 Upload Documents**
- Upload a single PDF or provide a directory path to load multiple PDFs.

### **🔍 Search & Query**
- Enter a search query to find relevant documents.
- Download the matched PDFs based on similarity scores.

### **❓ Q&A Assistant**
- Ask questions related to uploaded documents.
- Get AI-generated responses using Ollama LLM.

## Troubleshooting
### **Common Issues & Fixes**
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **API key errors**: Ensure `.env` is correctly configured.
- **File not found errors**: Verify the upload path and document directory.

## License

This project is licensed under the **GPL-3.0** License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have questions, suggestions, or issues, please:

- Open an issue on GitHub  
- Feel free to contact me at [hariprasath.m2017@gmail.com](mailto:hariprasath.m2017@gmail.com)

