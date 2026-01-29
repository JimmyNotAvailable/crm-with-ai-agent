"""
Build ChromaDB Index for RAG
Script để build/rebuild vector index từ data files
"""
import json
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from parser import parse_body_md, product_to_text

# =====================
# CONFIG
# =====================
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent.parent.parent
CHROMA_PATH = str(BASE_DIR / "chroma")
DATA_DIR = BASE_DIR / "data"
COLLECTION_NAME = "knowledge_base"

# Primary data sources (from scripts folder)
CLEANED_KB_FILE = PROJECT_ROOT / "scripts" / "cleaned_kb_articles.json"
CLEANED_PRODUCTS_FILE = PROJECT_ROOT / "scripts" / "cleaned_products.json"

# Legacy data sources (from local data folder)
POLICY_FILE = DATA_DIR / "policy_chunks.json"
PRODUCT_FILE = DATA_DIR / "cleaned_kb_articles.json"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def clean_metadata(meta: dict) -> dict:
    """Clean metadata to ensure ChromaDB compatibility"""
    cleaned = {}
    for k, v in meta.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            cleaned[k] = v
        else:
            cleaned[k] = str(v)
    return cleaned


def build_index(clear_existing: bool = True):
    """
    Build ChromaDB index from policy and product data
    
    Args:
        clear_existing: Whether to clear existing data before building
    """
    print(f"[BUILD] ChromaDB path: {CHROMA_PATH}")
    print(f"[BUILD] Collection: {COLLECTION_NAME}")
    
    # Init embedding function
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
    
    # Init ChromaDB client
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn
    )
    
    # Clear old data if requested
    if clear_existing:
        existing = collection.get(include=[])["ids"]
        if existing:
            collection.delete(ids=existing)
            print(f"[BUILD] Cleared {len(existing)} documents")
    
    # =====================
    # INGEST POLICY
    # =====================
    policy_count = 0
    if POLICY_FILE.exists():
        with open(POLICY_FILE, "r", encoding="utf-8") as f:
            policies = json.load(f)
        
        policy_docs, policy_metas, policy_ids = [], [], []
        
        for p in policies:
            if not p.get("id") or not p.get("content"):
                continue
            
            policy_docs.append(p["content"])
            policy_metas.append(clean_metadata({
                "type": "policy",
                "domain": p.get("metadata", {}).get("domain"),
                "topic": p.get("metadata", {}).get("topic"),
                "source": p.get("metadata", {}).get("source", "CRM")
            }))
            policy_ids.append(str(p["id"]))
        
        if policy_docs:
            collection.add(
                documents=policy_docs,
                metadatas=policy_metas,
                ids=policy_ids
            )
            policy_count = len(policy_docs)
        
        print(f"[BUILD] Policy docs ingested: {policy_count}")
    else:
        print(f"[BUILD] Policy file not found: {POLICY_FILE}")
    
    # =====================
    # INGEST PRODUCT (from cleaned_kb_articles.json in scripts folder)
    # =====================
    product_count = 0
    
    # Try cleaned KB file first (has body_md with full specs)
    product_source = CLEANED_KB_FILE if CLEANED_KB_FILE.exists() else PRODUCT_FILE
    
    if product_source.exists():
        print(f"[BUILD] Loading products from: {product_source}")
        with open(product_source, "r", encoding="utf-8") as f:
            products = json.load(f)
        
        if isinstance(products, dict):
            products = [products]
        
        product_docs, product_metas, product_ids = [], [], []
        
        for p in products:
            product_id = p.get("id") or p.get("_id")
            if not product_id:
                continue
            
            # Use product_to_text for body_md, fallback for other formats
            if p.get("body_md"):
                text = product_to_text(p)
            else:
                # Fallback for different product format
                text = f"""
Sản phẩm: {p.get("title") or p.get("name")}
Thương hiệu: {p.get("_meta", {}).get("brand") or p.get("brand")}
Danh mục: {p.get("_meta", {}).get("category") or p.get("category")}
Giá bán: {p.get("_meta", {}).get("price") or p.get("price")} VND
Mô tả: {p.get("description", "")}
""".strip()
            
            if not text:
                continue
            
            product_docs.append(text)
            product_metas.append(clean_metadata({
                "type": "product",
                "product_id": str(product_id),
                "code": p.get("code"),
                "title": p.get("title") or p.get("name"),
                "brand": p.get("_meta", {}).get("brand") or p.get("brand"),
                "category": p.get("_meta", {}).get("category") or p.get("category"),
                "price": p.get("_meta", {}).get("price") or p.get("price")
            }))
            product_ids.append(f"product_{product_id}")
        
        if product_docs:
            collection.add(
                documents=product_docs,
                metadatas=product_metas,
                ids=product_ids
            )
            product_count = len(product_docs)
        
        print(f"[BUILD] Product docs ingested: {product_count}")
    else:
        print(f"[BUILD] Product file not found: {PRODUCT_FILE}")
    
    # =====================
    # VERIFY
    # =====================
    print("\n[BUILD] === COMPLETED ===")
    print(f"[BUILD] Total documents: {collection.count()}")
    try:
        policy_in_db = len(collection.get(where={"type": "policy"})["ids"])
        product_in_db = len(collection.get(where={"type": "product"})["ids"])
        print(f"[BUILD] Policy count in DB: {policy_in_db}")
        print(f"[BUILD] Product count in DB: {product_in_db}")
    except Exception as e:
        print(f"[BUILD] Verify error: {e}")
    
    return {
        "policy_count": policy_count,
        "product_count": product_count,
        "total": collection.count()
    }


if __name__ == "__main__":
    result = build_index()
    print(f"\nResult: {result}")
