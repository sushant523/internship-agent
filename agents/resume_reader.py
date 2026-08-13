from pypdf import PdfReader


def read_resume(path):
    reader = PdfReader(str(path))

    text_parts = []

    for page in reader.pages:
        text_parts.append(page.extract_text() or "")

    return "\n".join(text_parts)