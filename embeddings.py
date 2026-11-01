from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL
model = SentenceTransformer(
    EMBEDDING_MODEL
)
VECTOR_SIZE = model.get_sentence_embedding_dimension()
def embed_text(text: str):
    return model.encode(text).tolist()
def embed_texts(texts: list[str]):
    return model.encode(texts).tolist()