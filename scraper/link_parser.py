import re
from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup

IGNORED_PREFIXES = ("mailto:", "tel:", "javascript:", "#")


class LinkParser:
    def is_pdf(self, url):
        """True si la ruta de la URL termina en .pdf (ignora ?parametros)."""
        return urlparse(url).path.lower().endswith(".pdf")

    def extract_links(self, html, base_url):
        """Devuelve dos listas de tuplas (url, texto_del_enlace).

        La primera tiene los enlaces a PDFs y la segunda los enlaces a otras
        páginas del mismo sitio, que el crawler puede seguir.
        """
        soup = BeautifulSoup(html, "html.parser")
        content = soup.select_one(".entry-content") or soup
        site = urlparse(base_url).netloc

        pdfs = []
        pages = []
        seen = set()

        for a in content.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(IGNORED_PREFIXES):
                continue

            url, _ = urldefrag(urljoin(base_url, href))
            if url in seen:
                continue
            seen.add(url)

            text = re.sub(r"\s+", " ", a.get_text(" ", strip=True))

            if self.is_pdf(url):
                pdfs.append((url, text))
            elif urlparse(url).netloc == site:
                pages.append((url, text))

        return pdfs, pages