import encodings.idna
import unicodedata
import re

def normalize_unicode(domain: str) -> str:
    """
    Normalizes domain by decoding IDNA (Punycode) to raw Unicode.
    """
    parts = domain.split('.')
    decoded_parts = []
    for p in parts:
        if p.startswith('xn--'):
            try:
                decoded_parts.append(p.encode('ascii').decode('idna'))
            except Exception:
                decoded_parts.append(p)
        else:
            decoded_parts.append(p)
            
    domain = '.'.join(decoded_parts)
    
   
    return domain

def preprocess_urls(urls: list) -> list:
    """
    Preprocess a list of URLs.
    Strips http/https, www., and paths to isolate the domain.
    Converts punycode to unicode.
    """
    cleaned = []
    for u in urls:
        u = str(u).strip().lower()
        u = re.sub(r'^https?://', '', u)
        u = re.sub(r'^www\.', '', u)
        u = u.split('/')[0]
        u = normalize_unicode(u)
        cleaned.append(u)
    return cleaned
