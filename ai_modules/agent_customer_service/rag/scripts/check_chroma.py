"""
Check ChromaDB - Script để kiểm tra trạng thái ChromaDB
"""
import chromadb
from pathlib import Path


def check_chroma():
    """Check ChromaDB status"""
    BASE_DIR = Path(__file__).resolve().parent.parent
    CHROMA_PATH = str(BASE_DIR / "chroma")
    COLLECTION_NAME = "knowledge_base"
    
    print(f"[CHECK] ChromaDB path: {CHROMA_PATH}")
    
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        
        # List collections
        collections = client.list_collections()
        print(f"[CHECK] Collections: {[c.name for c in collections]}")
        
        # Get our collection
        try:
            collection = client.get_collection(name=COLLECTION_NAME)
            total = collection.count()
            print(f"[CHECK] Collection '{COLLECTION_NAME}' has {total} documents")
            
            # Count by type
            try:
                policy_count = len(collection.get(where={"type": "policy"})["ids"])
                product_count = len(collection.get(where={"type": "product"})["ids"])
                print(f"[CHECK] - Policy: {policy_count}")
                print(f"[CHECK] - Product: {product_count}")
            except Exception as e:
                print(f"[CHECK] Count by type error: {e}")
                
        except Exception as e:
            print(f"[CHECK] Collection not found: {e}")
            
    except Exception as e:
        print(f"[CHECK] ChromaDB error: {e}")


if __name__ == "__main__":
    check_chroma()
