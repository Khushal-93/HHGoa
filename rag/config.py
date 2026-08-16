import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# HuggingFace Dataset
DATASET_REPO = os.getenv("DATASET_REPO", "ai4bharat/MSMARCO-XI")
DATASET_FILE = os.getenv("DATASET_FILE", "validation/hinval.parquet")

# Embedding Configuration
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-small"
)
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "
EMBEDDING_DIM = 384  # Dimension for multilingual-e5-small
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "64"))

# Retrieval Configuration
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))

# Persistence Paths
FAISS_INDEX_PATH = PROCESSED_DATA_DIR / "faiss_index.faiss"
METADATA_PATH = PROCESSED_DATA_DIR / "metadata.pkl"

# Device selection
import torch
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
