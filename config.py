import os 
from pathlib import Path 
 
from dotenv import load_dotenv 
 
load_dotenv() 
 
BASE_DIR = Path(__file__).resolve().parent 
 
UPLOAD_DIR = BASE_DIR / "data" / "uploads" 
UPLOAD_DIR.mkdir(parents=True, exist_ok=True) 
 
QDRANT_PATH = BASE_DIR / "qdrant_data" 
 
COLLECTION_NAME = "rag_documents" 
 
EMBEDDING_MODEL = ( 
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" 
) 
 
GROQ_MODEL = os.getenv( 
    "GROQ_MODEL", 
    "openai/gpt-oss-120b", 
) 
 
TOP_K = 4 
BRIEF_TOP_K = 6 
 
# Token-aware chunking. 
# The embedding model has a max sequence length of 128 tokens. 
CHUNK_SIZE = 100 
CHUNK_OVERLAP = 20