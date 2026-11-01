from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer
from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
)
tokenizer = AutoTokenizer.from_pretrained(
    EMBEDDING_MODEL
)
splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer,
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=[
        "\\n\\n",
        "\\n",
        ". ",
        " ",
        "",
    ],
)
def chunk_pages(pages, source: str):
    results = []
    for page in pages:
        chunks = splitter.split_text(
            page["text"]
        )
        for index, text in enumerate(chunks):
            results.append({
                "text": text,
                "source": source,
                "page": page["page"],
                "chunk_index": index,
            })
    return results