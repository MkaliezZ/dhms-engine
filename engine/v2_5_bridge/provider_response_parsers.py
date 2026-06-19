"""Response parsers for provider families."""


def parse_chat_completions(data):
    return str(data["choices"][0]["message"].get("content", ""))


def parse_openai_responses(data):
    if data.get("output_text"):
        return str(data["output_text"])
    parts = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and "text" in content:
                parts.append(str(content["text"]))
    return "\n".join(parts) if parts else str(data)


def parse_anthropic_messages(data):
    content = data.get("content", [])
    parts = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            parts.append(str(item.get("text", "")))
    return "\n".join(parts) if parts else str(data)


def parse_gemini_generate_content(data):
    return str(data["candidates"][0]["content"]["parts"][0].get("text", ""))


def parse_mistral_content(data):
    content = data["choices"][0]["message"].get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content)
