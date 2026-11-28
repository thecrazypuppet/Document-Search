from storage.database import connect


class FragmentRepository:
    def add_many(self, document_id, fragments):
        """Guarda los fragmentos de un documento.

        fragments es una lista de tuplas (pagina, texto_original, texto_normalizado).
        Si el documento ya tenía fragmentos, se borran antes para no duplicar.
        """
        conn = connect()
        conn.execute("DELETE FROM fragments WHERE document_id = ?", (document_id,))
        conn.executemany(
            "INSERT INTO fragments (document_id, page, original_text, normalized_text) "
            "VALUES (?, ?, ?, ?)",
            [
                (document_id, page, original, normalized)
                for page, original, normalized in fragments
            ],
        )
        conn.commit()
        conn.close()

    def list_all(self):
        """Todos los fragmentos junto con el nombre y la URL de su acta."""
        conn = connect()
        rows = conn.execute(
            """
            SELECT f.id, f.page, f.original_text, f.normalized_text,
                   d.link_text, d.pdf_url
            FROM fragments f
            JOIN documents d ON d.id = f.document_id
            ORDER BY f.id
            """
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]