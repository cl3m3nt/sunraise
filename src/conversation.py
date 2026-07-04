import base64
import json
from datetime import datetime
from pathlib import Path
from google.genai import types
from openai.types.responses import ResponseFunctionToolCall, ResponseReasoningItem
from anthropic.types import TextBlock, ToolUseBlock

_BYTES_KEY = "__bytes__"


# helper to debug conversation
def debug_conversation(current_messages, conversation):
    print("\n")
    print("Debug:")
    print("[current messages]:")
    print(current_messages)
    print("[conversation]:")
    print(conversation)
    print("\n")


def save_conversation(agent, conversation):
    """Save User/Agent conversation locally"""
    print("Saving conversation")
    folder_path = "conversation/conversation_" + datetime.now().strftime("%Y-%m-%d")
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    with open(
        f"{folder_path}/conversation_{agent.LLMProvider.name}_{timestamp}.json",
        "w",
    ) as f:
        json.dump(conversation, f)
    return f"{folder_path}/conversation_{agent.LLMProvider.name}_{timestamp}.json"


def _encode_bytes(obj):
    """Recursively replace bytes (e.g. thought_signature) with a base64 marker."""
    if isinstance(obj, bytes):
        return {_BYTES_KEY: base64.b64encode(obj).decode("ascii")}
    if isinstance(obj, dict):
        return {k: _encode_bytes(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_encode_bytes(v) for v in obj]
    return obj


def serialize_google_conversation(conversation):
    """Faithful, JSON-safe view of a mixed list (plain dicts + genai Content)."""
    out = []
    for item in conversation:
        if isinstance(item, types.Content):
            out.append(_encode_bytes(item.model_dump(exclude_none=True)))
        else:
            out.append(_encode_bytes(item))
    return out


def serialize_openai_conversation(conversation):
    """Helper to serialize ResponseFunctionToolCall from openai conversation"""
    out = []
    for c in conversation:
        if isinstance(c, (ResponseFunctionToolCall, ResponseReasoningItem)):
            # to_json() returns a JSON string; convert to a plain Python object for json.dump
            c = json.loads(c.to_json())
        # if type(c) in [ResponseFunctionToolCall, ResponseReasoningItem]:
        #   c = c.to_json()
        out.append(c)
    return out


def serialize_anthropic_conversation(conversation):
    """Helper to serialize TextBlock and ToolBlock from anthropic conversation"""
    out = []
    for c in conversation:
        new_blocks = []
        for block in c["content"]:
            if type(block) in [TextBlock, ToolUseBlock]:
                block = block.to_json()
                new_blocks.append(block)
            else:
                new_blocks.append(block)
        if new_blocks != c["content"]:
            c = {**c, "content": new_blocks}
        out.append(c)
    return out
