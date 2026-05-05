import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Opens a PDF and extracts text page by page.
    Returns a list of dicts with page number and text.
    """
    pages = []

    doc = fitz.open(file_path)  # open the PDF

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()   # extract raw text

        # Skip empty pages
        if text.strip():
            pages.append({
                "page_number": page_num,
                "text": text
            })

    doc.close()
    return pages


def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Takes extracted pages and splits them into smaller chunks.
    Each chunk remembers which page it came from.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,    # max 500 characters per chunk
        chunk_overlap=50   # 50 chars overlap to preserve context at edges
    )

    all_chunks = []

    for page in pages:
        # Split this page's text into chunks
        chunks = splitter.split_text(page["text"])

        for idx, chunk_text in enumerate(chunks):
            all_chunks.append({
                "content": chunk_text,
                "page_number": page["page_number"],
                "chunk_index": idx
            })

    return all_chunks


def process_pdf(file_path: str) -> list[dict]:
    """
    Full pipeline: PDF file → list of text chunks.
    This is the function we'll call from the background task.
    """
    print(f"📄 Extracting text from: {file_path}")
    pages = extract_text_from_pdf(file_path)
    print(f"✅ Extracted {len(pages)} pages")

    print(f"✂️  Chunking text...")
    chunks = chunk_pages(pages)
    print(f"✅ Created {len(chunks)} chunks")

    return chunks