from shared.logger import StepLogger
from rag_qa.ingestion import extract_text, chunk_text

logger = StepLogger()

with open("sample.txt", "rb") as f:
    text = extract_text(f, "sample.txt", logger)

chunks = chunk_text(text, logger)

for event in logger.get_events():
    print(event["timestamp"], event["stage"], "-", event["detail"])