from fastapi import FastAPI, Request
from pydantic import BaseModel

# Load model and tokenizer outside routes
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
model = AutoModelForCausalLM.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    torch_dtype=torch.float16,
    device_map="auto"
)

app = FastAPI()

class Query(BaseModel):
    instruction: str

@app.post("/generate")
def generate(query: Query):
    prompt = f"### Instruction:\n{query.instruction}\n\n### Response:\n"
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=100)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"output": response.split("### Response:")[-1].strip()}
