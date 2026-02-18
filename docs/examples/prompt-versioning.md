# Prompt Versioning Examples

This section demonstrates how to handle prompt versioning in your agents.

## Basic Prompt Versioning
Location: `examples/prompt_versioning/prompt_versioning_example.py`

This example shows how to manage different versions of prompts for your agents, allowing for experimentation and rollback capabilities.

```python
import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from langfuse import Langfuse
from kiboai.shared_kernel.logging import logger


def _extract_prompt_text(prompt_obj):
    for attr in ("prompt", "text", "content"):
        if hasattr(prompt_obj, attr):
            value = getattr(prompt_obj, attr)
            if value:
                return value
    if isinstance(prompt_obj, dict):
        return prompt_obj.get("prompt") or prompt_obj.get("text") or prompt_obj.get("content")
    return str(prompt_obj)


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    load_dotenv(os.path.join(repo_root, ".env"))

    host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")

    if not host or not public_key or not secret_key:
        logger.error("Missing Langfuse credentials. Check LANGFUSE_HOST/PUBLIC_KEY/SECRET_KEY.")
        return

    client = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host=host,
    )

    prompt_name = "kiboprompt"
    prompt_label = "production"

    try:
        prompt = client.get_prompt(name=prompt_name, label=prompt_label)
    except Exception as exc:
        logger.error("Failed to fetch prompt version: %s", exc)
        return

    prompt_text = _extract_prompt_text(prompt)
    logger.info("Prompt '%s' (%s): %s", prompt_name, prompt_label, prompt_text)


if __name__ == "__main__":
    main()
```

```bash
uv run examples/prompt_versioning/prompt_versioning_example.py
```
