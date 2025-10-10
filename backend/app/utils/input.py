def string_washer(text: str) -> str:
    text = text.strip().lower()
    new_text = ""
    for word in text.split(" "):
        if word != "":
            new_text += word
            new_text += " "
    return new_text.strip()