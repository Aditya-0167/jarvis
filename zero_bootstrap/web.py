import requests
from bs4 import BeautifulSoup

def fetch_public(url, max_chars=100000):
    if not url.startswith(("http://", "https://")):
        raise ValueError("Only public HTTP/HTTPS URLs are accepted.")
    r = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": "ZERO-Bootstrap/1.0"}
    )
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script","style","noscript","svg"]):
        tag.decompose()
    text = "\n".join(x.strip() for x in soup.get_text("\n").splitlines() if x.strip())
    return text[:max_chars]
