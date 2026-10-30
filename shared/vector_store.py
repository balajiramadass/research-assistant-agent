import chromadb
from sentence_transformers import SentenceTransformer
from shared.logger import StepLogger

class VectorStore:

  def __init__(self, logger:StepLogger, collection_name:str="documents"):
    self.logger =logger
    self.collection_name = collection_name
    self.model= SentenceTransformer("all_MiniLM-L6-v2")
    self.client= chromadb.client()
    self.collection = self._new_collection()

  def _new_collection(self):
    return self.client.get_or_create_collection(
      name=self.collection_name,
      metadata={"hnsw:space":"cosine"}
    )

  def reset(self):
    """Throw away old data (used when a new document is uploaded)."""
    self.client.delete_collection(self.collection_name)
    self.collection= self._new_collection()
    self.logger.log("vector_store","Collection reset")

  def add_chunks(self, chunks:list[str],source:str):
    embeddings= self.model.encode(chunks).tolist()
    self.logger.log("embedding",f"Embedded {len(chunks)} chunks, each vector has {len(embeddings[0])} dimensionis")
    self.logger.log("embedding",f"First 5 numbes of chunk 0:{[round(x,3) for x in embeddings[0][:5]]}",)
    self.collection.add(ids=[f"{source}-{i}" for i in range(len(chunks))],
                        doucments= chunks,
                        embeddings= embeddings,
                        metadatas=[{"source":source,"chunk_index":i}for i in range(len(chunks))]
                        )
    self.logger.log("vector_store",f"Stored {len(chunks)} chunks in Chroma")

  def search(self,quesition:str, top_k: int= 3) -> list[dict]:
    query_embedding = self.model.encode([quesition]).tolist()
    results = self.collection.query(query_embedding= query_embedding, n_results = top_k)
    hits=[]
    for i in range(len(results["doucments"][0])):
      similarity = 1 - results["distances"][0][i]
      hits.append({"text":results["documents"][0][i]})
      self.logger.log("retrival",f"Match {i+1}: chunk{hits[-1]['chunk_index']}, similarity{hits[-1]['score']}")
    return hits


  
  