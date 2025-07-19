import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models import Base
from ..models.key_value import Key, Val, KVRelation, KVSearch, create_kv_data, delete_kv_data

class TestKeyValue(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Create FTS5 table
        conn = self.engine.connect()
        conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS kv_search USING fts5(
            key, 
            key_id, 
            full_content, 
            tokenize='porter'
        )
        """)
        conn.close()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_delete_kv_data(self):
        # Create a KV entry
        key_text = "Test Key"
        val_list = ["Test Val 1", "Test Val 2"]
        key = create_kv_data(self.session, key_text, val_list)
        
        # Verify the data was created
        self.assertIsNotNone(key)
        self.assertEqual(key.key, key_text)
        
        # Get the created data for verification
        key_id = key.id
        relations = self.session.query(KVRelation).filter(KVRelation.key_id == key_id).all()
        val_ids = [relation.val_id for relation in relations]
        vals = self.session.query(Val).filter(Val.id.in_(val_ids)).all()
        kv_search = self.session.query(KVSearch).filter(KVSearch.key_id == key_id).first()
        
        # Verify all related data exists
        self.assertEqual(len(relations), 2)
        self.assertEqual(len(vals), 2)
        self.assertIsNotNone(kv_search)
        
        # Delete the KV entry
        delete_kv_data(self.session, key_id)
        
        # Verify all data has been deleted
        key_after = self.session.query(Key).filter(Key.id == key_id).first()
        relations_after = self.session.query(KVRelation).filter(KVRelation.key_id == key_id).all()
        vals_after = self.session.query(Val).filter(Val.id.in_(val_ids)).all()
        kv_search_after = self.session.query(KVSearch).filter(KVSearch.key_id == key_id).first()
        
        # Assert all data is deleted
        self.assertIsNone(key_after)
        self.assertEqual(len(relations_after), 0)
        self.assertEqual(len(vals_after), 0)
        self.assertIsNone(kv_search_after)
        
        print("[DEBUG_LOG] All KV data successfully deleted")

if __name__ == '__main__':
    unittest.main()