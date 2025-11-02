from langchain_community.vectorstores import FAISS
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from RAG.embeddings import generate_embeddings
from sentence_transformers import SentenceTransformer


def get_vector_store():
    try:
        embeddings = generate_embeddings()        
        index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        print("Vector DB initialized.")
        return vector_store
    except Exception as e:
        print("Vector not initailized , error :", e)


def search_vector_store(query: str):
    try:
        embeddings = generate_embeddings()
        vector_store = FAISS.load_local(
            "faiss_index", embeddings, allow_dangerous_deserialization=True
        )
        results = vector_store.similarity_search(query=query, k=7)
        print("Data found in VectorDB")
        return results
    except Exception as e:
        print(" -----> ", e)
