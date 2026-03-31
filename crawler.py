import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time


def crawl_website(base_url: str, max_pages: int = 10, max_chars: int = 15000) -> str:
    """
    Crawls a website starting from base_url, visiting up to max_pages pages.
    Returns all text content combined, trimmed to max_chars.
    """
    if not base_url.startswith("http"):
        base_url = "https://" + base_url

    visited = set()
    to_visit = [base_url]
    all_text = []
    domain = urlparse(base_url).netloc

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ChatbotCrawler/1.0)"
    }

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)

        if url in visited:
            continue

        try:
            response = requests.get(url, headers=headers, timeout=8)
            if response.status_code != 200:
                continue

            visited.add(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove noise elements
            for tag in soup(["script", "style", "nav", "footer", "header", "meta", "noscript"]):
                tag.decompose()

            # Extract clean text
            text = soup.get_text(separator=" ", strip=True)
            text = " ".join(text.split())  # collapse whitespace

            if text:
                all_text.append(f"[Page: {url}]\n{text}")

            # Find links on same domain
            for link in soup.find_all("a", href=True):
                href = urljoin(url, link["href"])
                parsed = urlparse(href)
                if (
                    parsed.netloc == domain
                    and href not in visited
                    and href not in to_visit
                    and parsed.scheme in ("http", "https")
                    and "#" not in href
                    and "?" not in href
                ):
                    to_visit.append(href)

            time.sleep(0.5)  # polite delay between requests

        except Exception:
            continue

    combined = "\n\n".join(all_text)
    return combined[:max_chars]
