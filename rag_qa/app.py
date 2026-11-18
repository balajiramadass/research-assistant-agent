import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from shared.logger import StepLogger
from shared.vector_store import VectorStore
from rag_qa.ingestion import extract_text, chunk_text
from rag_qa.answer import answer_questions
# ---------- One-time setup (survives re-runs) ----------
if "logger" not in st.session_state:
    st.session_state.logger = StepLogger()

if "store" not in st.session_state:
    with st.spinner("Loading embedding model (first time only)..."):
        st.session_state.store = VectorStore(st.session_state.logger)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed_key" not in st.session_state:
    st.session_state.processed_key = None

logger = st.session_state.logger
store = st.session_state.store

st.set_page_config(page_title="RAG Document QA", layout="wide")
st.title(" RAG Document QA")

with st.sidebar:
  st.header("Settings")
  chunk_size = st.slider("chunk size(characters)",200,1500,500, step=50)
  overlap= st.slider("Chunk overlap",0,150,50, step=10)
  top_k= st.slider("chunks to retrive (top_k)",1,6, 3)
  uploaded = st.file_uploader("Upload a document", type=["pdf","txt"])

if uploaded is not None:
  key =(uploaded.name, uploaded.size, chunk_size, overlap)
  if st.session_state.processed_key != key:
    logger.clear()
    st.session_state.messages =[]
    store.reset()
    with st.spinner("Reading, chunking and embedding"):
      text = extract_text(uploaded, uploaded.name, logger)
      if not text.strip():
        st.error("No text found, If this is a scanned PDF, it needs OCR")
        st.stop()
      chunks= chunk_text(text,logger, chunk_size=chunk_size, overlap=overlap)
      store.add_chunks(chunks, source=uploaded.name)

    st.session_state.processed_key=key

ready= st.session_state.processed_key is not None
question = st.chat_input("Ask something about your document" if ready else "upload a document first", disabled= not ready)

if question:
  st.session_state.messages.append({"role":"user", "content":question})
  with st.spinner("Retrieving and thinking"):
    try:
      answer,hits = answer_questions(question, store, logger, top_k=top_k)
    except Exception as e:
      logger.log("error",str(e))
      answer, hits =f"something went wrong: {e}",[]
  st.session_state.messages.append({"role":"assistant", "content":answer, "sources": hits})

col_chat, col_logs= st.columns([3,2])

with col_chat:
  st.subheader("Chat")
  if not ready:
    st.info(" Upload a PDF or .txt file in the sidebar to begin")
  for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
      st.write(msg["content"])
      if msg.get("sources"):
        with st.expander("Retrived Chunks"):
          for h in msg["sources"]:
            st.markdown(f"**Chunk {h['chunk_index']} **(similarity {h['score']})")
            st.caption(h["text"])

ICONS = {
    "extraction": "📥", "chunking": "✂️", "embedding": "🧮",
    "vector_store": "🗄️", "retrieval": "🔍", "prompt": "📝",
    "llm_call": "🤖", "answer": "✅", "error": "❌",
}

with col_logs:
  st.subheader("What happened")
  with st.expander("show me what happened", expanded= True):
    events= logger.get_events()
    if not events:
      st.write("No events yet")
    for e in events:
      icon= ICONS.get(e["stage"], ".")
      st.markdown(f"'{e['timestamp']}' {icon} **{e['stage']}**")
      st.caption(e["detail"])
      