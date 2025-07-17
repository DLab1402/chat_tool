import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.Client()
collection = client.get_or_create_collection("rag_docs", embedding_function=embedding_function)

with open("D:/LAB/MCP_BCONS/Task3n11/data/RAG.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Chia nhỏ thành các đoạn (chunk) theo 2 dòng trống hoặc theo logic bạn muốn
chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]

for i, chunk in enumerate(chunks):
    collection.add(documents=[chunk], ids=[f"doc_{i}"])

print("✅ Đã tạo vector database từ RAG.txt.")
