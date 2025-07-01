import os
import numpy as np
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
import google.generativeai as genai

# Set Gemini API key from environment variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")


class PolicyQueryHandler:
    def __init__(
        self,
        persist_dir="chroma_store",
        embedding_model_name="all-MiniLM-L6-v2",
        top_k=3,
    ):
        # LangChain-compatible embedding wrapper
        self.embedder = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            encode_kwargs={"normalize_embeddings": True},
        )

        # Chroma DB setup with LangChain embedding wrapper
        self.vectordb = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embedder,
        )

        self.top_k = top_k

    def semantic_search(self, query, top_k=1):
        top_k = top_k or self.top_k
        results = self.vectordb.similarity_search(query, k=top_k)
        return results

    def rerank_results(self, query, docs):
        query_emb = self.embedder.embed_query(query)
        scored_docs = []

        for doc in docs:
            doc_emb = self.embedder.embed_query(doc.page_content)
            score = np.dot(query_emb, doc_emb) / (
                np.linalg.norm(query_emb) * np.linalg.norm(doc_emb)
            )
            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs]

    def create_prompt(self, query, contexts):
        context_text = "\n\n".join(
            [f"Context {i+1}: {doc.page_content}" for i, doc in enumerate(contexts)]
        )
        prompt = (
            "You are a helpful assistant. Use the following policy document excerpts to answer the question:\n\n"
            f"{context_text}\n\n"
            f"Question: {query}\n"
            "Answer:"
        )
        return prompt

    def get_response(self, query):
        docs = self.semantic_search(query)
        reranked_docs = self.rerank_results(query, docs)
        prompt = self.create_prompt(query, reranked_docs[:self.top_k])

        response = gemini_model.generate_content(prompt)
        return response.text.strip()
