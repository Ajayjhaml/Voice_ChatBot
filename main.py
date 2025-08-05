from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig
import torch

# ==== Load Model ====
# Path to the LoRA adapter directory
adapter_path = "tinyllama-lora-out"  # Change to your LoRA adapter folder

# Load adapter config to get base model path
adapter_config = PeftConfig.from_pretrained(adapter_path)
base_model_id = adapter_config.base_model_name_or_path

# Load base model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model_id)
base_model = AutoModelForCausalLM.from_pretrained(base_model_id, torch_dtype=torch.float32)

# Load fine-tuned LoRA adapter
model = PeftModel.from_pretrained(base_model, adapter_path)
model.eval()

# ==== FastAPI App ====
app = FastAPI(
    title="Tiny LLaMA Alpaca API",
    description="Serve fine-tuned TinyLLaMA Alpaca-style model via FastAPI",
    version="1.0"
)

# ==== Request Body Schema ====
class GenerationRequest(BaseModel):
    instruction: str
    input: str = ""
    max_tokens: int = 128
    temperature: float = 0.7

# ==== Format Prompt as Alpaca ====
def format_prompt(instruction: str, input_text: str) -> str:
    if input_text.strip():
        return f"""### Instruction:
{instruction}

### Input:
{input_text}

### Response:"""
    else:
        return f"""### Instruction:
{instruction}

### Response:"""

# ==== Inference Route ====
@app.post("/generate")
def generate_text(request: GenerationRequest):
    prompt = format_prompt(request.instruction, request.input)
    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            do_sample=True,
            top_p=0.95,
            top_k=50,
            pad_token_id=tokenizer.eos_token_id,
        )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Cut the prompt from the output
    if "### Response:" in result:
        result = result.split("### Response:")[-1].strip()

    return {"response": result}
