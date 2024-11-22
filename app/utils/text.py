import re
import unicodedata

def slugify(text: str) -> str:
    print(type(text))
    if not isinstance(text, str):
        raise TypeError("slugify function expects a string as input")
    
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    return text