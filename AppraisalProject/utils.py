# app/utils.py
import io, os
from typing import Iterable
from PIL import Image
from PyPDF2 import PdfMerger

ALLOWED_IMG = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
ALLOWED_PDF = {".pdf"}

def _guess_ext(name: str) -> str:
    return os.path.splitext(name)[1].lower()

def merge_uploads_to_pdf(files: Iterable, out_fobj) -> None:
    """
    files: iterable of InMemoryUploadedFile / TemporaryUploadedFile
    out_fobj: a writable binary file-like (open(..., 'wb'))
    """
    merger = PdfMerger()
    temp_buffers = []

    for f in files:
        if not f:
            continue
        ext = _guess_ext(f.name)
        # PDF → append directly
        if ext in ALLOWED_PDF:
            merger.append(f)
        # Image → convert to single-page PDF in memory, then append
        elif ext in ALLOWED_IMG:
            img = Image.open(f).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="PDF")   # auto page size based on image
            buf.seek(0)
            temp_buffers.append(buf)
            merger.append(buf)
        else:
            # ignore unsupported files silently (or raise)
            continue

    merger.write(out_fobj)
    merger.close()
    # buffers auto GC; no disk temp files used
