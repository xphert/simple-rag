import json
import os

import httpx

from config import GROQ_MODEL

# Endpoint OpenAI-compatible (Groq, gateway, LiteLLM, dsb).
LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY") or None

# Base URL harus diakhiri "/v1" (contoh: https://api.groq.com/openai/v1).
# Kosong berarti memakai endpoint Groq resmi.
LLM_BASE_URL = (os.getenv("LLM_BASE_URL") or "").strip().rstrip("/") or (
    "https://api.groq.com/openai/v1" if LLM_API_KEY else ""
)
LLM_MODEL = os.getenv("LLM_MODEL") or GROQ_MODEL

# Parameter generation yang diuji pada Experiment 1.
# Nilai default repository: 0.2
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# Dipakai hanya jika tidak ada API key: model lokal (offline).
LOCAL_MODEL = os.getenv(
    "LLM_LOCAL_MODEL",
    "models/Qwen2.5-1.5B-Instruct",
)
LOCAL_MAX_NEW_TOKENS = int(os.getenv("LLM_MAX_NEW_TOKENS", "220"))

# URL chat completions yang dipanggil. None = mode lokal.
LLM_CHAT_URL = f"{LLM_BASE_URL}/chat/completions" if LLM_API_KEY else None
BACKEND = (
    f"remote:{LLM_BASE_URL}"
    if LLM_CHAT_URL
    else f"local:{LOCAL_MODEL}"
)

_local = {}


def _load_local():
    if "model" in _local:
        return _local["tokenizer"], _local["model"]
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
    )

    torch.set_num_threads(os.cpu_count() or 4)
    tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        LOCAL_MODEL,
        dtype="auto",
    )
    model.eval()
    _local["tokenizer"] = tokenizer
    _local["model"] = model
    return tokenizer, model


def _generate_local(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
) -> str:
    import torch

    tokenizer, model = _load_local()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer(prompt, return_tensors="pt")
    options = {
        "max_new_tokens": LOCAL_MAX_NEW_TOKENS,
        "pad_token_id": tokenizer.eos_token_id,
        "repetition_penalty": 1.15,
    }
    if temperature > 0:
        options.update(
            do_sample=True,
            temperature=temperature,
            top_p=0.9,
        )
    else:
        # temperature 0.0 = greedy decoding, hasil deterministik.
        options.update(do_sample=False)
    with torch.no_grad():
        output = model.generate(**inputs, **options)
    generated = output[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(
        generated,
        skip_special_tokens=True,
    ).strip()


async def _generate_remote(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
) -> str:
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "temperature": temperature,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=180) as http:
        response = await http.post(
            LLM_CHAT_URL,
            headers={"Authorization": f"Bearer {LLM_API_KEY}"},
            json=payload,
        )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        raise RuntimeError(
            f"LLM endpoint error {error.response.status_code}: "
            f"{error.response.text[:300]}"
        ) from error

    # Sebagian gateway mengabaikan stream=False dan tetap mengirim SSE.
    if "text/event-stream" in response.headers.get("content-type", ""):
        parts = []
        for line in response.text.splitlines():
            if line.startswith("data: ") and line != "data: [DONE]":
                chunk = json.loads(line[6:])
                parts.append(chunk["choices"][0]["delta"].get("content") or "")
        return "".join(parts).strip()

    return (response.json()["choices"][0]["message"].get("content") or "").strip()


async def generate_text(
    system_prompt: str,
    user_prompt: str,
    temperature: float | None = None,
):
    if temperature is None:
        temperature = TEMPERATURE
    if LLM_CHAT_URL is None:
        return _generate_local(
            system_prompt,
            user_prompt,
            temperature,
        )
    return await _generate_remote(
        system_prompt,
        user_prompt,
        temperature,
    )
