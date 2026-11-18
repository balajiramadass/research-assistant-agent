from shared.llm import call_claude
from shared.logger import StepLogger
from shared.vector_store import VectorStore

SYSTEM_PROMPT=("you answe questions using only the context provided."
               "if the answe is not in the context say: I coun't find that in the document.")

def answer_questions(question:str, store:VectorStore, logger:StepLogger, top_k: int=3):
  hits=store.search(question, top_k= top_k)
  context ="\n\n".join(f"[chunk{h['chunk_index']}]\n {h['text']}" for h in hits)
  logger.log("prompt", f"Built context from {len(hits)} chunks({len(context)}characters)")

  user_message=f"Context:\n{context} \n\nQuestion:{question}"
  answer= call_claude(SYSTEM_PROMPT, user_message, logger)
  logger.log("answer",answer)
  return answer, hits
