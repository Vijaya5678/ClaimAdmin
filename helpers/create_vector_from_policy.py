from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from langchain.embeddings import HuggingFaceEmbeddings


def index_pdf_to_chroma(
    pdf_path: str = "kb/policy.pdf",
    persist_dir: str = "chroma_store"
):
    # 1. Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # 2. Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_documents(documents)

    # 3. Create HuggingFace embedding model
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_model = HuggingFaceEmbeddings(model_name=model_name)

    # 4. Store in ChromaDB
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,  # ✅ Pass this once
        persist_directory=persist_dir
    )

    vectordb.persist()
    print(f"✅ Indexed '{pdf_path}' into Chroma at '{persist_dir}'.")

if __name__ == "__main__":
    index_pdf_to_chroma()
