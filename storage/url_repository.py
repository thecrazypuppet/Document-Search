from storage.database import connect


class UrlRepository:
    def add(self, url):
        """Guarda una URL. Devuelve True si era nueva, False si ya existía."""
        url = url.strip()
        if not url:
            return False
        conn = connect()
        cursor = conn.execute("INSERT OR IGNORE INTO urls (url) VALUES (?)", (url,))
        conn.commit()
        nueva = cursor.rowcount == 1
        conn.close()
        return nueva

    def list_all(self):
        conn = connect()
        rows = conn.execute("SELECT url FROM urls ORDER BY id").fetchall()
        conn.close()
        return [row["url"] for row in rows]