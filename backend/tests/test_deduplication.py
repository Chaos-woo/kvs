from flask import Flask
import sys
from pathlib import Path

# Add the parent directory to the Python path if it's not already there
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from models import SessionLocal, Base, engine
from models.key_value import Key, Val, KVRelation, KVSearch, create_kv_data, search_kv_data, create_fts5_table

# Initialize database
Base.metadata.create_all(bind=engine)
create_fts5_table()

def test_deduplication():
    db = SessionLocal()
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(KVRelation).delete()
        db.query(Val).delete()
        db.query(Key).delete()
        
        # Execute raw SQL to clear the FTS5 table
        from sqlalchemy import text
        db.execute(text("DELETE FROM kv_search"))
        
        db.commit()
        print("Data cleared.")
        
        # Create test data that will produce duplicate results in search
        print("\nCreating test data...")
        # Create a key that will match both in key and content searches
        key1 = create_kv_data(db, "test_key", ["test_content"])
        # Create another key that will only match in content search
        key2 = create_kv_data(db, "another_key", ["test_content"])
        print("Test data created.")
        
        # Verify the data was created
        keys = db.query(Key).all()
        print(f"\nTotal keys after creating test data: {len(keys)}")
        for key in keys:
            print(f"Key - id: {key.id}, key: {key.key}")
            
            # Get the vals for this key
            relations = db.query(KVRelation).filter(KVRelation.key_id == key.id).all()
            val_ids = [relation.val_id for relation in relations]
            vals = db.query(Val).filter(Val.id.in_(val_ids)).all()
            print(f"  Vals: {[val.val for val in vals]}")
        
        # Check FTS5 table
        conn = db.connection().connection
        cursor = conn.cursor()
        cursor.execute("SELECT rowid, key, key_id, full_content FROM kv_search")
        kv_search_entries = cursor.fetchall()
        print(f"\nTotal entries in kv_search table: {len(kv_search_entries)}")
        for entry in kv_search_entries:
            print(f"KVSearch - rowid: {entry[0]}, key: {entry[1]}, key_id: {entry[2]}, full_content: {entry[3]}")
        
        # Test search with a query that will match both in key and content
        print("\nTesting search with query='test'...")
        results = search_kv_data(db, "test")
        print(f"\nSearch results count: {len(results)}")
        
        # Check for duplicates
        result_ids = [result.id for result in results]
        unique_ids = set(result_ids)
        print(f"Unique IDs in results: {len(unique_ids)}")
        
        if len(result_ids) == len(unique_ids):
            print("PASS: No duplicates found in search results.")
        else:
            print("FAIL: Duplicates found in search results.")
            # Print the duplicates
            from collections import Counter
            id_counts = Counter(result_ids)
            duplicates = [id for id, count in id_counts.items() if count > 1]
            print(f"Duplicate IDs: {duplicates}")
        
        # Print the results
        for result in results:
            print(f"Result - id: {result.id}, key: {result.key}")
            
            # Get the vals for this result
            relations = db.query(KVRelation).filter(KVRelation.key_id == result.id).all()
            val_ids = [relation.val_id for relation in relations]
            vals = db.query(Val).filter(Val.id.in_(val_ids)).all()
            print(f"  Vals: {[val.val for val in vals]}")
        
    except Exception as e:
        print(f"Error in test_deduplication: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_deduplication()