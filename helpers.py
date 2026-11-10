import io
import logging
import os
from google import genai
from google.genai import types
from pypdf import PdfReader
from extensions import db
from flask_login import current_user
from models import Subject

MAX_CHARS = 30000   # longest text sent to Gemini
MAX_PAGES = 50      # most PDF pages read


def get_user_subject(subject_id):
    """Return the subject if it belongs to the logged-in user, else 404."""
    return db.first_or_404(
        db.select(Subject).where(
            Subject.id == subject_id,
            Subject.user_id == current_user.id
        ))


class SummaryError(Exception):
    pass


def extract_text(file):
    """Read text from an uploaded .txt or .pdf."""
    filename = (file.filename or "").lower()
    data = file.read()

    if not data:
        raise SummaryError("The file is empty.")

    if filename.endswith(".txt"):
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            raise SummaryError("Text files must be UTF-8 encoded.")

    elif filename.endswith(".pdf"):
        # real PDFs start with these bytes, whatever the file is named
        if not data.startswith(b"%PDF"):
            raise SummaryError("That file is not a valid PDF.")
        try:
            reader = PdfReader(io.BytesIO(data))
            if reader.is_encrypted:
                raise SummaryError("Password-protected PDFs are not supported.")
            pages = [page.extract_text() or "" for page in reader.pages[:MAX_PAGES]]
        except SummaryError:
            raise
        except Exception:
            raise SummaryError("Could not read that PDF.")
        text = "\n".join(pages)

    else:
        raise SummaryError("Only PDF or TXT files are supported.")

    text = text.strip()
    if not text:
        raise SummaryError("No readable text found. Scanned PDFs (images) are not supported.")

    return text[:MAX_CHARS]


def summarize(text):
    """Send text to Gemini and return the summary."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SummaryError("The summarizer is not configured (missing API key).")

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You summarize a student's study notes. Write a concise summary "
                    "as short bullet points, one per line, starting each with '- '. "
                    "Use only information from the notes and do not add new facts."
                )
            ),
        )
        summary = (response.text or "").strip()
    except Exception:
        logging.exception("Gemini request failed")
        raise SummaryError("Could not generate a summary right now. Please try again.")

    if not summary:
        raise SummaryError("The model returned an empty summary. Please try again.")

    return summary