from __future__ import annotations
import os
from typing import Optional, Dict, Any
import httpx

# 简单的提供商抽象：OpenAI 兼容 / Ollama
class LLMProvider:
    def __init__(self, model: str, provider: str | None = None):
        self.model = model
        self.provider = (provider or os.getenv("PROVIDER") or "openai").lower()
        if self.provider == "openai":
            from openai import OpenAI
            base_url = os.getenv("OPENAI_BASE_URL")  # 支持 OpenAI 兼容端点
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=base_url)
        elif self.provider == "ollama":
            # 使用 httpx 调用本地 ollama
            self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            self.client = httpx.Client(timeout=120)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def completion(self, messages: list[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1024) -> str:
        if self.provider == "openai":
            # Chat Completions 风格的统一接口
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return resp.choices[0].message.content
        elif self.provider == "ollama":
            # 调用 /api/chat，与 OpenAI 风格近似
            payload = {
                "model": self.model,
                "messages": messages,
                "options": {"temperature": temperature, "num_predict": max_tokens}
            }
            r = self.client.post(f"{self.ollama_host}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
            # ollama 流式时是 event-stream；这里假设一次性返回（简化）
            if isinstance(data, dict) and "message" in data:
                return data["message"].get("content", "")
            # 有些版本会以累积块返回
            if isinstance(data, list):
                return "".join(chunk.get("message", {}).get("content", "") for chunk in data)
            return ""
        else:
            raise RuntimeError("Unknown provider")
