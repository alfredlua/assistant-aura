import os
import numpy as np
from dotenv import load_dotenv 
import google.generativeai as genai
import pickle

load_dotenv()
gemini_api_key=os.getenv("GOOGLE_GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

embedding_model = "models/text-embedding-004"

class SimpleVectorDB():
  def __init__(self, file_path="vector_db.pkl"):
    self.file_path = file_path
    if os.path.exists(file_path):
      with open(file_path, 'rb') as f:
        self.data = pickle.load(f)
    else:
      self.data = {"embeddings": [], "chunks": []}

  def chunk_document(self, text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
      end = start + chunk_size
      chunk = text[start:end]
      chunks.append(chunk)
      start = end - overlap
    return chunks
  
  def get_embedding(self, text):
    return genai.embed_content(model=embedding_model, content=text)["embedding"]
    
  def add_document(self, document):
    chunks = self.chunk_document(document)
    for chunk in chunks:
      embedding = self.get_embedding(chunk)
      self.data["embeddings"].append(embedding)
      self.data["chunks"].append(chunk)
    self.save()

  def find_most_relevant(self, query_embedding, top_k=1):
    embeddings = np.array(self.data["embeddings"])
    similarities = np.dot(embeddings, query_embedding)
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return [self.data["chunks"][i] for i in top_indices]
  
  def save(self):
    with open(self.file_path, "wb") as f:
      pickle.dump(self.data, f)