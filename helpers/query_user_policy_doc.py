# query_policy_documents.py

import os
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
import google.generativeai as genai
from dotenv import load_dotenv

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

class PolicyDocQuery:
    def __init__(self, persist_base="chroma_docs"):
        self.persist_base = persist_base
        self.embedder = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            encode_kwargs={"normalize_embeddings": True}
        )

    def query(self, policy_id, question, k=3):
        db_path = os.path.join(self.persist_base, policy_id)
        if not os.path.exists(db_path):
            return "⚠️ No documents found for this policy."

        vectordb = Chroma(
            persist_directory=db_path,
            embedding_function=self.embedder
        )

        docs = vectordb.similarity_search(question, k=k)
        if not docs:
            return "🤷 No relevant information found in your documents."

        context = "\n\n".join([doc.page_content for doc in docs])
        prompt = (
            "You are a helpful assistant. Based on the following documents, answer the user's question:\n\n"
            f"{context}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )

        response = gemini_model.generate_content(prompt)
        return response.text.strip()
