from pypdf import PdfReader
from shared.logger import StepLogger

def extract_text(file, filename:str, logger:StepLogger) -> str:
  """Turn an uploaded file (PDF or .txt) into one big string."""
  if filename.lower().endswith(".pdf"):
    reader=PdfReader(file)
    pages=[page.extract_text() or "" for page in reader.pages]
    text="\n".join(pages)
    logger.log("extraction",f"PDF'{filename}': {len(reader.pages)} pages, {len(text)} characters")
  else:
    text= file.read().decode("utf-8")
    logger.log("extraction", f"Text file '{filename}': {len(text)} characters")
    return text

def chunk_text(text:str, logger:StepLogger, chunk_size: int =500, overlap:int = 50) -> list[str]:
  """Split text into fixed-size pieces that overlap slightly."""
  chunks=[]
  step= chunk_size-overlap
  start =0
  while start < len(text):
    chunks.append(text[start:start +chunk_size])
    start += step

  logger.log("chunking",f"Created {len(chunks)} chunks(size={chunk_size}),overlap={overlap}")

  for i, chunk in enumerate(chunks[:3]):
    logger.log("chunking", f"Chunk {i} preview: {chunk[:60]!r}...")
  return chunks
