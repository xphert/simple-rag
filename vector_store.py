from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)
from config import (
    COLLECTION_NAME,
    QDRANT_PATH,
)
from embeddings import VECTOR_SIZE
qdrant = QdrantClient(
    path=str(QDRANT_PATH)
)
if not qdrant.collection_exists(
    collection_name=COLLECTION_NAME
):
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )
def store_chunks(
    chunks: list[dict],
    vectors: list[list[float]],
):
    points = []
    for chunk, vector in zip(chunks, vectors):
        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload=chunk,
            )
        )
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )
    return len(points)
def search_chunks(
    query_vector: list[float],
    limit: int,
):
    response = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True,
    )
    results = []
    for point in response.points:
        payload = point.payload or {}
        results.append({
            "text": payload.get("text", ""),
            "source": payload.get("source", ""),
            "page": payload.get("page"),
            "chunk_index": payload.get("chunk_index"),
            "score": float(point.score),
        })
    return results