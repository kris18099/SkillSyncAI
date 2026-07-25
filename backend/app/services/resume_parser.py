import re
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO

import pdfplumber
from docx import Document

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "rtf", "odt"}


class UnsupportedResumeType(ValueError):
    """Raised when an upload is not a supported resume document."""


def extract_resume_text(filename: str, content: bytes) -> str:
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix not in ALLOWED_EXTENSIONS:
        raise UnsupportedResumeType(
            "Unsupported file format. Please upload a PDF, DOCX, DOC, RTF, or ODT file."
        )

    if suffix == "pdf":
        return _extract_pdf(content)
    if suffix == "docx":
        return _extract_docx(content)
    if suffix == "doc":
        return _extract_doc(content)
    if suffix == "rtf":
        return _extract_rtf(content)
    if suffix == "odt":
        return _extract_odt(content)

    raise UnsupportedResumeType(
        "Unsupported file format. Please upload a PDF, DOCX, DOC, RTF, or ODT file."
    )


def _extract_pdf(content: bytes) -> str:
    with pdfplumber.open(BytesIO(content)) as pdf:
        pages = [(page.extract_text() or "").strip() for page in pdf.pages]
    return "\n\n".join(page for page in pages if page).strip()


def _extract_docx(content: bytes) -> str:
    document = Document(BytesIO(content))
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs]
    return "\n".join(paragraph for paragraph in paragraphs if paragraph).strip()


def _extract_doc(content: bytes) -> str:
    """Extracts text from legacy MS Word .doc files."""
    try:
        return _extract_docx(content)
    except Exception:
        pass

    # Fallback binary text extraction for OLE .doc format
    text_utf16 = content.decode("utf-16le", errors="ignore")
    words_utf16 = re.findall(r"[\x20-\x7E\u00A0-\u024F]{3,}", text_utf16)

    text_ascii = content.decode("latin-1", errors="ignore")
    words_ascii = re.findall(r"[\x20-\x7E]{3,}", text_ascii)

    ignore_keywords = {
        "WordDocument",
        "Root Entry",
        "CompObj",
        "ObjectPool",
        "SummaryInformation",
        "DocumentSummaryInformation",
        "Table",
        "Data",
        "Microsoft Word",
    }

    selected = words_utf16 if len(" ".join(words_utf16)) > len(" ".join(words_ascii)) else words_ascii
    cleaned = [
        w.strip()
        for w in selected
        if w.strip() not in ignore_keywords and len(w.strip()) > 2
    ]
    return "\n".join(cleaned).strip()


def _extract_rtf(content: bytes) -> str:
    """Extracts text from Rich Text Format (.rtf) files."""
    try:
        from striprtf.striprtf import rtf_to_text

        text_str = content.decode("utf-8", errors="ignore")
        extracted = rtf_to_text(text_str).strip()
        if extracted:
            return extracted
    except Exception:
        pass

    # Regex fallback for stripping RTF tags
    text_str = content.decode("latin-1", errors="ignore")
    text_str = re.sub(r"\{\\\*(?:[^{}]+|\{[^{}]*\})*\}", "", text_str)
    text_str = re.sub(r"\{\\(?:fonttbl|stylesheet|info|header|footer)[^{}]*\}", "", text_str)
    text_str = re.sub(r"\\[a-zA-Z]+-?\d*\s?", " ", text_str)
    text_str = re.sub(r"[{}]", "", text_str)
    lines = [line.strip() for line in text_str.splitlines() if line.strip()]
    return "\n".join(lines).strip()


def _extract_odt(content: bytes) -> str:
    """Extracts text from OpenDocument Text (.odt) files."""
    with zipfile.ZipFile(BytesIO(content)) as zip_file:
        xml_bytes = zip_file.read("content.xml")
    root = ET.fromstring(xml_bytes)
    texts = []
    for elem in root.iter():
        if elem.text and elem.text.strip():
            texts.append(elem.text.strip())
        if elem.tail and elem.tail.strip():
            texts.append(elem.tail.strip())
    return "\n".join(texts).strip()