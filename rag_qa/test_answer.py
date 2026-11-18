from shared.logger import StepLogger
from shared.vector_store import VectorStore
from rag_qa.ingestion import extract_text, chunk_text
from rag_qa.answer import answer_questions
logger= StepLogger()

with open("sample.txt", "rb") as f:
  text= extract_text(f,"sample.txt", logger)

chunks= chunk_text(text,logger, chunk_size=300, overlap=50)

store= VectorStore(logger)
store.add_chunks(chunks, source="sample.text")

answer, hits= answer_questions("What is the capital of France?", store, logger)

for event in logger.get_events():
  print(event["timestamp"], event["stage"],"-", event["detail"])
