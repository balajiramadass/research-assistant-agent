import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["ANTHROPIC_API_KEY"]
API_URL = "https://api.anthropic.com/v1/messages"

def call_claude(messages, system_prompt):
  print("Roles in order:", [m["role"] for m in messages])  
  headers={
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
   
  }
  body={
         "model": "claude-sonnet-4-6", 
         "max_tokens": 1024,
        "system": system_prompt,
        "messages": messages,
         "stop_sequences": ["Observation:"]
  }

  resp= requests.post(API_URL, headers=headers, json=body, timeout=30)
  print(f"llm call --------request{body}")
  if not resp.ok:
    print("API error body:", resp.text)
  resp.raise_for_status()
  data= resp.json()
  print("\n=== RAW API RESPONSE ===")
  print("RAW TEXT (repr):", repr(data["content"]))
  print("=== END RAW RESPONSE ===\n")
  return data["content"][0]["text"].rstrip() 

if __name__=="__main__":
  from prompt import SYSTEM_PROMPT
  out = call_claude([{"role":"user","content":"What is the Eiffel Tower's Completion Year?"}], SYSTEM_PROMPT)
  print(out)