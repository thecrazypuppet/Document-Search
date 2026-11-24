from config import BASE_DIR
from storage.database import connect


class DocumentRepository:
    def exists(self, pdf_url):
        """True si la URL está registrada Y el archivo sigue en la carpeta."""
        conn = connect()
        row = conn.execute(
            "SELECT local_path FROM documents WHERE pdf_url = ?", (pdf_url,)
        ).fetchone()
        conn.close()
        return row is not None and (BASE_DIR / row["local_path"]).exists()

    def exists_hash(self, sha256):
        """True si hay un documento con el mismo contenido y su archivo sigue en la carpeta."""
        conn = connect()
        rows = conn.execute(
            "SELECT local_path FROM documents WHERE sha256 = ?", (sha256,)
        ).fetchall()
        conn.close()
        return any((BASE_DIR / row["local_path"]).exists() for row in rows)

    def add(self, pdf_url, link_text, local_path, sha256):
        """Guarda un documento descargado y devuelve su id."""
        conn = connect()
        conn.execute(
            """
            INSERT INTO documents (pdf_url, link_text, local_path, sha256)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(pdf_url) DO UPDATE SET
                link_text = excluded.link_text,
                local_path = excluded.local_path,
                sha256 = excluded.sha256,
                status = 'descargado',
                error = NULL
            """,
            (pdf_url, link_text, local_path, sha256),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id FROM documents WHERE pdf_url = ?", (pdf_url,)
        ).fetchone()
        conn.close()
        return row["id"]

    def list_pending(self):
        """Documentos descargados que todavía no se indexan."""
        conn = connect()
        rows = conn.execute(
            "SELECT id, pdf_url, link_text, local_path FROM documents "
            "WHERE status = 'descargado' ORDER BY id"
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def mark_indexed(self, doc_id):
        conn = connect()
        conn.execute(
            "UPDATE documents SET status = 'indexado', error = NULL WHERE id = ?",
            (doc_id,),
        )
        conn.commit()
        conn.close()

    def mark_failed(self, doc_id, motivo):
        conn = connect()
        conn.execute(
            "UPDATE documents SET status = 'fallido', error = ? WHERE id = ?",
            (motivo, doc_id),
        )
        conn.commit()
        conn.close()