from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os
import transformers
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import HfApi

# Load environment variables
load_dotenv()
hf_token = os.getenv("HUGGINGFACE_API_KEY")

if not hf_token:
    raise ValueError("HUGGINGFACE_API_KEY not found in environment variables.")

api = HfApi(token=hf_token)
whoami_info = api.whoami()
print("Logged in as:", whoami_info["name"])

class Message(BaseModel):
    role: str
    content: str

class GenerateRequest(BaseModel):
    messages: List[Message]
    max_new_tokens: int = 256

app = FastAPI()

model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

# Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id, use_auth_token=hf_token)

# Check and add pad_token if necessary
if tokenizer.pad_token is None:
    print("Pad token not found. Adding a pad token.")
    tokenizer.add_special_tokens({'pad_token': '<|pad|>'})
    pad_token_id = tokenizer.pad_token_id
    print(f"Added pad token: {tokenizer.pad_token}, with id: {pad_token_id}")
else:
    pad_token_id = tokenizer.pad_token_id
    print(f"Pad token already set: {tokenizer.pad_token}, with id: {pad_token_id}")

# Load the model
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", use_auth_token=hf_token)

# Resize token embeddings if pad_token was added
if tokenizer.pad_token is not None and model.config.pad_token_id is None:
    print("Resizing model's token embeddings to include the new pad token.")
    model.resize_token_embeddings(len(tokenizer))
    model.config.pad_token_id = pad_token_id
    print(f"Model's pad_token_id set to: {model.config.pad_token_id}")

# print("Model loaded.", model)
# print("Tokenizer loaded.", tokenizer)

# Initialize the pipeline with the updated pad_token_id
print("Loading the pipeline...")
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    model_kwargs={
        "torch_dtype": torch.bfloat16,
        "pad_token_id": pad_token_id,  # Use the newly defined pad_token_id
    },
    device_map="auto",
)
print("Pipeline loaded.")

@app.post("/generate")
def generate(req: GenerateRequest):
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    outputs = pipeline(messages, max_new_tokens=req.max_new_tokens)
    generated_text = outputs[0]["generated_text"]
    return {"generated_text": generated_text}
