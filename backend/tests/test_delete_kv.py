import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.key_value import Key, Val, KVRelation, KVSearch, create_kv_data, delete_kv_data

# Create SQLAlchemy engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_delete_kv():
    """Test that delete_kv_data properly deletes all associated data"""
    db = SessionLocal()
    try:
        # Create a KV entry
        key_text = "Test Key"
        val_list = ["Test Val 1", "Test Val 2"]
        print(f"[DEBUG_LOG] Creating KV entry with key '{key_text}' and values {val_list}")

        key = create_kv_data(db, key_text, val_list)
        key_id = key.id
        print(f"[DEBUG_LOG] Created KV entry with key_id {key_id}")

        # Verify the data was created
        relations = db.query(KVRelation).filter(KVRelation.key_id == key_id).all()
        val_ids = [relation.val_id for relation in relations]
        vals = db.query(Val).filter(Val.id.in_(val_ids)).all()
        kv_search = db.query(KVSearch).filter(KVSearch.key_id == key_id).first()

        print(f"[DEBUG_LOG] Found {len(relations)} relations")
        print(f"[DEBUG_LOG] Found {len(vals)} values")
        print(f"[DEBUG_LOG] Found FTS entry: {kv_search is not None}")

        # Delete the KV entry
        print(f"[DEBUG_LOG] Deleting KV entry with key_id {key_id}")
        delete_kv_data(db, key_id)

        # Verify all data has been deleted
        key_after = db.query(Key).filter(Key.id == key_id).first()
        relations_after = db.query(KVRelation).filter(KVRelation.key_id == key_id).all()
        vals_after = db.query(Val).filter(Val.id.in_(val_ids)).all()
        kv_search_after = db.query(KVSearch).filter(KVSearch.key_id == key_id).first()

        print(f"[DEBUG_LOG] Key after deletion: {key_after is not None}")
        print(f"[DEBUG_LOG] Relations after deletion: {len(relations_after)}")
        print(f"[DEBUG_LOG] Values after deletion: {len(vals_after)}")
        print(f"[DEBUG_LOG] FTS entry after deletion: {kv_search_after is not None}")

        if key_after is None and len(relations_after) == 0 and len(vals_after) == 0 and kv_search_after is None:
            print("[DEBUG_LOG] SUCCESS: All KV data was properly deleted")
        else:
            print("[DEBUG_LOG] FAILURE: Some KV data was not deleted")
            if key_after is not None:
                print(f"[DEBUG_LOG] Key still exists: {key_after.id}")
            if len(relations_after) > 0:
                print(f"[DEBUG_LOG] Relations still exist: {len(relations_after)}")
            if len(vals_after) > 0:
                print(f"[DEBUG_LOG] Values still exist: {len(vals_after)}")
            if kv_search_after is not None:
                print(f"[DEBUG_LOG] FTS entry still exists: {kv_search_after.key_id}")

    except Exception as e:
        print(f"[DEBUG_LOG] Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_delete_kv()
