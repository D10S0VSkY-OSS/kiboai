from typing import Any, Dict, List, Optional
from mem0 import Memory
from mem0.configs.base import MemoryConfig, VectorStoreConfig, LlmConfig, EmbedderConfig
import os


class KiboMemory:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KiboMemory, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        """Initialize Mem0 with local ChromaDB configuration by default."""
        try:
            # Configure Vector Store (Chroma)
            vector_store_config = VectorStoreConfig(
                provider="chroma",
                config={
                    "collection_name": "kibo_memory",
                    "path": "./kibo_chroma_db",
                    "host": os.getenv("CHROMA_HOST", "localhost"),
                    "port": int(os.getenv("CHROMA_PORT", 8000)),
                },
            )

            # Create Memory Config

            # Mem0 relies on OpenAI by default.
            # We configure it to use the Kibo Proxy (LiteLLM) which maps these models to actual providers.
            # We ensure API Key and Base URL are set in environment for the OpenAI client to pick them up.

            # Ensure we have at least a dummy key if none provided, to pass basic checks.
            if not os.getenv("OPENAI_API_KEY"):
                os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-proxy"

            # Set base URL to proxy if not set
            if not os.getenv("OPENAI_BASE_URL"):
                os.environ["OPENAI_BASE_URL"] = "http://localhost:4000"

            embedder_config = EmbedderConfig(
                provider="openai",
                config={
                    "model": "text-embedding-3-small",
                    "http_client_proxies": None,  # Avoid interference
                },
            )

            llm_config = LlmConfig(
                provider="openai", config={"model": "gpt-4o-mini", "temperature": 0.1}
            )

            config = MemoryConfig(
                vector_store=vector_store_config,
                embedder=embedder_config,
                llm=llm_config,
            )

            # Initialize Memory
            try:
                # Try direct instantiation first
                self.memory = Memory(config=config)
            except Exception as e:
                print(f"Error: Failed to initialize Memory with config: {e}")
                print(
                    "Tip: Ensure 'kibo start db' is running if using ChromaDB server."
                )
                # Do NOT fallback to default Memory() as it uses invalid models for our proxy.
                self.memory = None
                raise e  # Re-raise to stop execution or let caller handle
        except Exception as e:
            print(f"Critical Error initializing KiboMemory: {e}")
            self.memory = None

    def add(self, messages, user_id, **kwargs):
        if self.memory:
            return self.memory.add(messages, user_id=user_id, **kwargs)
        print("Error: Memory not initialized.")
        return None

    def get(self, query, user_id, **kwargs):
        if self.memory:
            return self.memory.get(query, user_id=user_id, **kwargs)
        return None

    def search(self, query, user_id, **kwargs):
        if self.memory:
            return self.memory.search(query, user_id=user_id, **kwargs)
        return None

    def get_all(self, user_id, **kwargs):
        if self.memory:
            return self.memory.get_all(user_id=user_id, **kwargs)
        return None
