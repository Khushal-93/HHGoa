"""
scripts/export_onnx.py — One-time export of multilingual-e5-small to ONNX.

Run this once before starting the server (or after cloning a fresh repo):

    py -3.13 scripts/export_onnx.py

The exported model is saved to:
    data/processed/e5_small_onnx/model.onnx

Once present, rag/embeddings.py automatically routes embed_query() calls
through ONNX Runtime for ~3x lower embedding latency (P50 ~24 ms vs ~80 ms).

Requirements:
    onnxruntime    (pip install onnxruntime)
    onnxscript     (pip install onnxscript)
    sentence-transformers
    torch
"""
import sys
import time
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from rag.config import EMBEDDING_MODEL_NAME, PROCESSED_DATA_DIR

ONNX_DIR = PROCESSED_DATA_DIR / "e5_small_onnx"
ONNX_PATH = ONNX_DIR / "model.onnx"

ONNX_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Export: multilingual-e5-small → ONNX Runtime")
print("=" * 60)

if ONNX_PATH.exists():
    print(f"Model already exists at {ONNX_PATH}. Delete it to re-export.")
    sys.exit(0)

import torch
from sentence_transformers import SentenceTransformer

print("Loading PyTorch model (first-time load may take ~15 s)...")
t0 = time.perf_counter()
model_pt = SentenceTransformer(EMBEDDING_MODEL_NAME, device="cpu")
print(f"  Loaded in {(time.perf_counter()-t0)*1000:.0f} ms")

backbone = model_pt._first_module().auto_model
backbone.eval()
tokenizer = model_pt.tokenizer

sample = tokenizer(
    "query: What is a corporation?",
    return_tensors="pt",
    padding=True,
    truncation=True,
    max_length=128,
)

print(f"Exporting to {ONNX_PATH} ...")
t0 = time.perf_counter()
with torch.no_grad():
    torch.onnx.export(
        backbone,
        (sample["input_ids"], sample["attention_mask"]),
        str(ONNX_PATH),
        input_names=["input_ids", "attention_mask"],
        output_names=["last_hidden_state"],
        dynamic_axes={
            "input_ids":         {0: "batch", 1: "seq_len"},
            "attention_mask":    {0: "batch", 1: "seq_len"},
            "last_hidden_state": {0: "batch", 1: "seq_len"},
        },
        opset_version=18,
    )
size_kb = ONNX_PATH.stat().st_size // 1024
print(f"  Export complete in {(time.perf_counter()-t0)*1000:.0f} ms")
print(f"  ONNX model: {ONNX_PATH} ({size_kb} KB)")
print()
print("Done. rag/embeddings.py will now auto-select ONNX Runtime for embed_query().")
