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

def test_fts5_search():
    db_session = SessionLocal()
    try:
        # Try to query the FTS5 table directly
        query = '1'
        conn = db_session.connection().connection  # Get the underlying SQLite connection
        cursor = conn.cursor()
        try:
            # Try the syntax used in search_kv_data
            print("[DEBUG_LOG] Trying search_kv_data syntax for key...")
            query_with_wildcard = query + "*"
            cursor.execute(
                "SELECT key_id FROM kv_search WHERE kv_search MATCH ?",
                (f"key:{query_with_wildcard}",)
            )
            key_matches = cursor.fetchall()
            print(f"[DEBUG_LOG] Key MATCH result: {key_matches}")
        except Exception as e:
            print(f"[DEBUG_LOG] Error in key MATCH query: {str(e)}")

        try:
            # Try the syntax used in search_kv_data for full_content
            print("[DEBUG_LOG] Trying search_kv_data syntax for full_content...")
            query_with_wildcard = query + "*"
            cursor.execute(
                "SELECT key_id FROM kv_search WHERE kv_search MATCH ?",
                (f"full_content:{query_with_wildcard}",)
            )
            content_matches = cursor.fetchall()
            print(f"[DEBUG_LOG] Content MATCH result: {content_matches}")
        except Exception as e:
            print(f"[DEBUG_LOG] Error in content MATCH query: {str(e)}")

        try:
            # Try a simpler FTS5 syntax
            print("[DEBUG_LOG] Trying simpler FTS5 syntax...")
            query_with_wildcard = query + "*"
            cursor.execute(
                "SELECT * FROM kv_search WHERE kv_search MATCH ?",
                (query_with_wildcard,)
            )
            simple_matches = cursor.fetchall()
            print(f"[DEBUG_LOG] Simple MATCH result: {simple_matches}")
        except Exception as e:
            print(f"[DEBUG_LOG] Error in simple MATCH query: {str(e)}")

        # Use empty lists if queries failed
        key_matches = []
        content_matches = []

        # Combine the results
        matching_key_ids = list(set(key_matches + content_matches))

        # Get the corresponding keys
        if matching_key_ids:
            keys = db_session.query(Key).filter(Key.id.in_(matching_key_ids)).all()

    except Exception as e:
        print(f"Error in test_fts5_search: {str(e)}")
    finally:
        db_session.close()

if __name__ == "__main__":
    test_fts5_search()
