import warnings
warnings.filterwarnings(
    "ignore",
    message=".*clean_up_tokenization_spaces.*",
    category=FutureWarning
)

from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import random

collection_name = "imdb_reviews"
model_name = "sentence-transformers/all-MiniLM-L6-v2"

client = QdrantClient(host="qdrant", port=6333)

# Delete and recreate collection
try:
    client.delete_collection(collection_name=collection_name)
except Exception:
    pass

dataset = load_dataset("imdb", split="train")
dataset = dataset.shuffle(seed=random.randint(0, 10000)).select(range(2000))

model = SentenceTransformer(model_name)

client.create_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
)

vectors = model.encode(dataset["text"])
points = [
    models.PointStruct(
        id=i,
        vector=vectors[i],
        payload={"text": dataset["text"][i], "label": dataset["label"][i]}
    )
    for i in range(len(dataset))
]
client.upsert(collection_name=collection_name, points=points)

pos_count = sum(1 for lbl in dataset["label"] if lbl == 1)
neg_count = sum(1 for lbl in dataset["label"] if lbl == 0)
print(f"✅ Loaded {len(dataset)} IMDB reviews into Qdrant "
      f"({pos_count} positives, {neg_count} negatives)")