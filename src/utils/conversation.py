from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI
import os
import google.generativeai as genai
load_dotenv()

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")     # Studio key
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY    # for SDKs that read env only
genai.configure(api_key=GOOGLE_API_KEY, transport="rest")
# Load credentials securely
MONGO_URI = os.getenv("DB_CONNECTION_URL")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = "vectorstore"
DB_INDEX_NAME = "default"

# MongoDB setup
client = MongoClient(MONGO_URI)
collection = client[DB_NAME][COLLECTION_NAME]

class Response:
    def __init__(self, query):
        self.query = query

    def get_response(self) -> str:
        user_query: str = self.query.lower()

        # Step 1: Create query embeddings using Gemini via LangChain
        embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            task_type="retrieval_query",
            google_api_key=GOOGLE_API_KEY,
        )

        try:
            query_vector = embedding_model.embed_query(user_query)
        except Exception as e:
            return f"Embedding failed: {e}"

        # Step 2: MongoDB Atlas vector search with correct syntax
        try:
            pipeline = [
                {
                    "$search": {
                        "knnBeta": {
                            "vector": query_vector,
                            "path": "embedding",
                            "k": 5
                        }
                    }
                },
                {
                    "$project": {
                        "text": 1,
                        "_score": {"$meta": "searchScore"},
                        "source": 1
                    }
                }
            ]

            results = list(collection.aggregate(pipeline))
            # return results

            if not results:
                return "No relevant documents found."

            # Step 3: Prepare context
            context = "\n\n".join(doc.get("text", "") for doc in results)

            # Step 4: Generate answer
            prompt = f"""
                You are a helpful AI assistant specialist in Document Summarization.

                Your rules:
                - Only use the content provided in the documents to answer.
                - Do NOT make assumptions or add external information.
                - Always remember previous document interactions to maintain context.
                - If the answer is not found in the context, clearly state so.

                IMPORTANT:
                - Your response should be strctured format either pointer or summary.

                Use the following documents to answer the question:

                {context}

                Question: {user_query}
                Answer:
            """
            response = GoogleGenerativeAI(model="gemini-2.0-flash", max_tokens=2500, temperature=0.2)
            return response.invoke(prompt)

        except Exception as e:
            return f"MongoDB vector search failed: {e}"