def string_washer(text: str) -> str:
    return " ".join([w for w in text.strip() if w != " "]).lower()