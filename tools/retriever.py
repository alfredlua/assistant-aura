
def get_tasks(query: str, db: str):
  from loop import db
  """
  Get information about past tasks and results using a RAG system.
  
  Args:
    query: The user's query.
    db: The database instance.
  
  Returns:
    A string that contains information about past tasks.
  """
  if len(db.data['embeddings']) == 0:
    return "There is no previous task or result."
  query_embedding = db.get_embedding(query)
  relevant_chunks = db.find_most_relevant(query_embedding, top_k=2)

  context = "\n".join(relevant_chunks)
  return context
