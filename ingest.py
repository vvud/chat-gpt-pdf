import pdfplumber
import PyPDF4
import re
import os
import sys
from typing import Callable, List, Tuple, Dict

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import fitz

from dotenv import load_dotenv


def extract_metadata_from_pdf(file_path: str) -> dict:
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF4.PdfFileReader(pdf_file)  # Change this line
        metadata = reader.getDocumentInfo()
        return {
            "title": metadata.get("/Title", "").strip(),
            "author": metadata.get("/Author", "").strip(),
            "creation_date": metadata.get("/CreationDate", "").strip(),
        }


def extract_pages_from_pdf(file_path: str) -> List[Tuple[int, str]]:
    """
    Extracts the text from each page of the PDF.

    :param file_path: The path to the PDF file.
    :return: A list of tuples containing the page number and the extracted text.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    doc = fitz.open(file_path)
    pages = []

    for page in doc:
        text = page.get_text()
        if text.strip():  # Check if extracted text is not empty
            pages.append((page.number, text))
    return pages


def parse_pdf(file_path: str) -> Tuple[List[Tuple[int, str]], Dict[str, str]]:
    """
    Extracts the title and text from each page of the PDF.

    :param file_path: The path to the PDF file.
    :return: A tuple containing the title and a list of tuples with page numbers and extracted text.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    metadata = extract_metadata_from_pdf(file_path)
    pages = extract_pages_from_pdf(file_path)

    return pages, metadata


def merge_hyphenated_words(text: str) -> str:
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


def fix_newlines(text: str) -> str:
    return re.sub(r"(?<!\n)\n(?!\n)", " ", text)


def remove_multiple_newlines(text: str) -> str:
    return re.sub(r"\n{2,}", "\n", text)


def clean_text(
    pages: List[Tuple[int, str]], cleaning_functions: List[Callable[[str], str]]
) -> List[Tuple[int, str]]:
    cleaned_pages = []
    for page_num, text in pages:
        for cleaning_function in cleaning_functions:
            text = cleaning_function(text)
        cleaned_pages.append((page_num, text))
    return cleaned_pages


def text_to_docs(text: List[str], metadata: Dict[str, str]) -> List[Document]:
    """Converts list of strings to a list of Documents with metadata."""
    doc_chunks = []

    for page_num, page in text:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            chunk_overlap=200,
        )
        chunks = text_splitter.split_text(page)
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "page_number": page_num,
                    "chunk": i,
                    "source": f"p{page_num}-{i}",
                    **metadata,
                },
            )
            doc_chunks.append(doc)

    return doc_chunks


if __name__ == "__main__":
    load_dotenv()

    # Step 1: Parse PDF, declare start and end page
    file_path = "data/honda.pdf"
    start_page = 2
    end_page = 130

    raw_pages, metadata = parse_pdf(file_path)

    # Step 2: Create text chunks
    cleaning_functions = [
        merge_hyphenated_words,
        fix_newlines,
        remove_multiple_newlines,
    ]
    cleaned_text_pdf = clean_text(raw_pages, cleaning_functions)

    document_chunks = text_to_docs(cleaned_text_pdf, metadata)

    # Optional: Reduce embedding cost by only using the first (end_page-start_page) pages
    # document_chunks = document_chunks[start_page - 1 : end_page - 1]

    # Step 3 + 4: Generate embeddings and store them in DB
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(
        document_chunks,
        embeddings,
        collection_name="honda-book",
        persist_directory="data/chroma",
    )

    # Save DB locally
    vector_store.persist()
