# index_policy_documents.py

import os
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def index_documents_for_policy(policy_id, docs_path="data/documents", persist_base="chroma_docs"):
    full_path = os.path.join(docs_path, policy_id)
    if not os.path.exists(full_path):
        return {"error": f"No folder found for policy {policy_id}"}

    embedder = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        encode_kwargs={"normalize_embeddings": True}
    )
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    all_docs = []
    for file in os.listdir(full_path):
        if file.lower().endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(full_path, file))
            pages = loader.load_and_split()
            all_docs.extend(pages)

    chunks = splitter.split_documents(all_docs)
    db_path = os.path.join(persist_base, policy_id)

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embedder,
        persist_directory=db_path
    )
    vectordb.persist()

    return {"success": f"Indexed {len(chunks)} chunks for policy {policy_id}"}


# EXAMPLE USAGE
if __name__ == "__main__":
    policy_id = "IND-2025-0001"
    result = index_documents_for_policy(policy_id)
    print(result)
