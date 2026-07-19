from langchain_ollama.chat_models import ChatOllama

from .tools import get_tools

llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=1.0,
).bind_tools(get_tools())
