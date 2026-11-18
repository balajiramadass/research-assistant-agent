import os
import requests
from dotenv import load_dotenv
from shared.logger import StepLogger

load_dotenv()

API_KEY = os.environ["ANTHROPIC_API_KEY"]
API_URL = "https://api.anthropic.com/v1/messages"



def call_claude(system :str, user_message:str,logger:StepLogger, model:str ="claude-sonnet-5-5", max_tokens:int =500) -> str:
  
  headers={
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
   
  }
  body={
         "model": model, 
         "max_tokens": max_tokens,
         "system": system,
         "messages": [{"role":"user", "content":user_message}],
         "stop_sequences": ["Observation:"]
  }

  logger.log("llm_call", f"Sending request to {model}")
  resp= requests.post(API_URL, headers=headers, json=body, timeout=30)
  print(f"llm call --------request{body}")
  if not resp.ok:
    print("API error body:", resp.text)
  resp.raise_for_status()
  data= resp.json()
  print("\n=== RAW API RESPONSE ===")
  print("RAW TEXT (repr):", repr(data["content"]))
  print("=== END RAW RESPONSE ===\n")
  answer =data["content"][0]["text"].rstrip()
  usage = data["usage"]
  logger.log("llm_call", f"Answer received: {usage['input_tokens']} input tokens, {usage['output_tokens']} output tokens")

  return answer

if __name__=="__main__":
  from prompt import SYSTEM_PROMPT
  out = call_claude([{"role":"user","content":"What is the Eiffel Tower's Completion Year?"}], SYSTEM_PROMPT)
  print(out)