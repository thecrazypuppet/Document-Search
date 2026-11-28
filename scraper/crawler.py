import time
from collections import deque
from urllib.parse import urlparse

import requests

import config
from scraper.link_parser import LinkParser

USER_AGENT = "Document-Search (proyecto escolar)"


class Crawler:
    def __init__(self, downloader, parser=None):
        self.downloader = downloader
        self.parser = parser or LinkParser()
        self.visited = set()
        self.seen_pdfs = set()
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT

    def crawl(self, start_url):
        """Recorre el sitio desde start_url y descarga los PDFs que encuentre.

        Devuelve un resumen con contadores.
        """
        summary = {
            "paginas": 0,
            "pdfs": 0,
            "descargados": 0,
            "omitidos": 0,
            "errores": 0,
        }
        site = urlparse(start_url).netloc
        queue = deque([(start_url, 0)])

        while queue:
            url, depth = queue.popleft()
            if url in self.visited:
                continue
            self.visited.add(url)

            page = self._fetch_page(url)
            if page is None:
                summary["errores"] += 1
                continue

            final_url, html = page
            self.visited.add(final_url)
            summary["paginas"] += 1
            print(f"[nivel {depth}] {final_url}")

            pdfs, pages = self.parser.extract_links(html, final_url)

            for pdf_url, text in pdfs:
                if pdf_url in self.seen_pdfs:
                    continue
                self.seen_pdfs.add(pdf_url)
                summary["pdfs"] += 1
                self._download(pdf_url, text, summary)

            if depth < config.MAX_DEPTH:
                for page_url, _ in pages:
                    if self._is_allowed(page_url, site):
                        queue.append((page_url, depth + 1))

        return summary

    def _is_allowed(self, url, site):
        """Solo páginas http(s) del mismo sitio y que no se hayan visitado."""
        parts = urlparse(url)
        return (
            parts.scheme in ("http", "https")
            and parts.netloc == site
            and url not in self.visited
        )

    def _fetch_page(self, url):
        """Devuelve (url_final, html) o None si la página no se pudo leer."""
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as error:
            print(f"  No se pudo abrir {url}: {error}")
            return None
        finally:
            time.sleep(config.DELAY_SECONDS)

        if "html" not in response.headers.get("Content-Type", "").lower():
            print(f"  Se omite {url}: no es una página HTML")
            return None

        return response.url, response.text

    def _download(self, pdf_url, text, summary):
        try:
            status, detail = self.downloader.download(pdf_url, text)
        except Exception as error:
            status, detail = "error", str(error)

        if status == "descargado":
            summary["descargados"] += 1
        elif status == "omitido":
            summary["omitidos"] += 1
        else:
            summary["errores"] += 1

        print(f"  [{status}] {text or pdf_url} {detail}")

        if status != "omitido":
            time.sleep(config.DELAY_SECONDS)