#!/usr/bin/env python3
"""Call an OpenAI-compatible chat API to propose the next experiment config.

Reads the AutoResearch prompt from stdin and prints only TOML to stdout.
Required environment variables:
  OPENAI_ENDPOINT    Base endpoint, e.g. https://api.example.com/v1
  OPENAI_API_KEY     API key for Bearer auth
  OPENAI_MODEL_NAME  Model name understood by the endpoint
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse


def getenv_required(name):
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def chat_completions_url(endpoint):
    endpoint = endpoint.rstrip("/")
    if endpoint.endswith("/chat/completions"):
        return endpoint
    return endpoint + "/chat/completions"


def curl_resolve_args(url):
    resolve_ip = os.environ.get("OPENAI_RESOLVE_IP")
    if not resolve_ip:
        return []
    parsed = urllib.parse.urlparse(url)
    if not parsed.hostname:
        raise SystemExit(f"Cannot infer hostname from OPENAI_ENDPOINT: {url}")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return ["--resolve", f"{parsed.hostname}:{port}:{resolve_ip}"]


def extract_text(response):
    choices = response.get("choices") or []
    if not choices:
        raise ValueError("API response did not contain choices")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") in {"text", "output_text"}:
                parts.append(item.get("text", ""))
        return "\n".join(parts)
    raise ValueError("API response did not contain message.content text")


def strip_markdown_fence(text):
    match = re.search(r"```(?:toml)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    return (match.group(1) if match else text).strip()


def main():
    prompt = sys.stdin.read()
    if not prompt.strip():
        raise SystemExit("Expected AutoResearch prompt on stdin")

    endpoint = getenv_required("OPENAI_ENDPOINT")
    api_key = getenv_required("OPENAI_API_KEY")
    model = getenv_required("OPENAI_MODEL_NAME")
    temperature = float(os.environ.get("OPENAI_TEMPERATURE", "0.7"))
    max_tokens = int(os.environ.get("OPENAI_MAX_TOKENS", "8192"))

    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You propose TOML config files for diffusion sampler experiments. "
                    "Return only valid TOML with [proposal] and [sampler] sections. "
                    "Do not include markdown fences or explanatory text."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }

    url = chat_completions_url(endpoint)
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as request_file:
        json.dump(payload, request_file)
        request_file.flush()
        proc = subprocess.run(
            [
                "curl",
                "--silent",
                "--show-error",
                "--retry",
                "3",
                "--retry-delay",
                "1",
                "--max-time",
                "120",
                *curl_resolve_args(url),
                url,
                "-H",
                f"Authorization: Bearer {api_key}",
                "-H",
                "Content-Type: application/json",
                "--data-binary",
                f"@{request_file.name}",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    if proc.returncode != 0:
        raise SystemExit(f"curl failed with exit code {proc.returncode}:\n{proc.stderr}\n{proc.stdout}")

    toml_text = strip_markdown_fence(extract_text(json.loads(proc.stdout)))
    if "[proposal]" not in toml_text or "[sampler]" not in toml_text:
        raise SystemExit("Model response did not contain both [proposal] and [sampler] sections")
    print(toml_text)


if __name__ == "__main__":
    main()
