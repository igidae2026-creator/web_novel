import os, time, inspect
from openai import OpenAI

class LLM:
    def __init__(self, cfg: dict):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY is not set.")
        timeout_seconds = float(
            (cfg.get("model", {}) or {}).get(
                "request_timeout_seconds",
                (cfg.get("limits", {}) or {}).get("request_timeout_seconds", 180),
            )
            or 180
        )
        self.client = OpenAI(api_key=api_key, timeout=timeout_seconds)
        self.model = cfg["model"]["name"]
        self.max_retries = int(cfg["limits"].get("max_retries", 4))
        self.mode = cfg["model"].get("mode", "batch").lower()
        self.timeout_seconds = timeout_seconds

    def call(self, prompt: str, temperature: float = 0.7):
        last_err = None
        for i in range(self.max_retries):
            try:
                kwargs = dict(model=self.model, input=prompt, temperature=temperature)
                # Best-effort: attempt priority tier if supported by SDK/server
                if self.mode == "priority":
                    # some SDKs accept service_tier or priority
                    kwargs.update({"service_tier": "priority"})
                resp = self.client.responses.create(**kwargs)
                return resp
            except TypeError:
                # fallback without service_tier
                try:
                    resp = self.client.responses.create(model=self.model, input=prompt, temperature=temperature)
                    return resp
                except Exception as e:
                    last_err = e
            except Exception as e:
                last_err = e
            time.sleep(0.8 * (2 ** i))
        raise last_err
