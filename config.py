from pathlib import Path

BASE_DIR = Path(file).resolve().parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
DB_PATH = DATA_DIR / "actas.db"

START_URL = "https://fi-ing.unison.mx/actas/"

MAX_DEPTH = 3
DELAY_SECONDS = 1.0
REQUEST_TIMEOUT = 15
MIN_SCORE = 0.6