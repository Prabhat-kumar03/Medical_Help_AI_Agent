# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

def generate_embeddings():
    try:
        # embeddings = FakeEmbeddings(size=1352)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return embeddings
    except Exception as e:
        print("Unable to process Embeddings", e)
