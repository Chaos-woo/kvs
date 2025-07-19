#!/usr/bin/env python3
"""
Test script for KV export functionality (direct database test)
"""
import sys
import os
import json
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_export_functionality():
    print("Testing KV Export Functionality (Direct Database Test)")
    print("=" * 60)
    
    try:
        # Import backend modules
        from models import SessionLocal
        from models.key_value import Key, Val, KVRelation
        
        print("\n1. Testing Database Connection:")
        db = SessionLocal()
        
        # Check if there's any data in the database
        key_count = db.query(Key).count()
        val_count = db.query(Val).count()
        relation_count = db.query(KVRelation).count()
        
        print(f"   Keys in database: {key_count}")
        print(f"   Values in database: {val_count}")
        print(f"   Relations in database: {relation_count}")
        
        if key_count == 0:
            print("\n   No data found. Creating sample data for testing...")
            # Create sample data
            from models.key_value import create_kv_data
            
            # Create some test KV pairs
            create_kv_data(db, "test_key_1", ["value1", "value2"])
            create_kv_data(db, "test_key_2", ["value3"])
            create_kv_data(db, "test_key_3", ["value4", "value5", "value6"])
            
            print("   Sample data created successfully!")
            
            # Recount after creating data
            key_count = db.query(Key).count()
            val_count = db.query(Val).count()
            relation_count = db.query(KVRelation).count()
            
            print(f"   Updated counts - Keys: {key_count}, Values: {val_count}, Relations: {relation_count}")
        
        print("\n2. Testing Export Stats Logic:")
        # Test export stats logic
        unique_k_count = db.query(Key).count()
        total_v_count = db.query(Val).count()
        total_kv_pairs = db.query(KVRelation).count()
        
        stats_result = {
            "k_count": unique_k_count,
            "v_count": total_v_count,
            "kv_pairs_count": total_kv_pairs
        }
        
        print(f"   Export Stats: {json.dumps(stats_result, indent=4)}")
        
        print("\n3. Testing Export Data Logic:")
        # Test export data logic
        keys_query = db.query(Key).all()
        export_data = []
        
        for key in keys_query:
            # Get all relations for this key
            relations = db.query(KVRelation).filter(KVRelation.key_id == key.id).all()
            
            if relations:
                # Get all values for this key
                val_ids = [relation.val_id for relation in relations]
                vals = db.query(Val).filter(Val.id.in_(val_ids)).all()
                val_texts = [val.val for val in vals]
                
                # Use the earliest creation time from the relations as the create_at timestamp
                earliest_relation = min(relations, key=lambda r: r.created_at)
                create_at = earliest_relation.created_at.isoformat()
                
                # Create the export record in the specified format
                export_record = {
                    "k": key.key,
                    "v": val_texts,
                    "create_at": create_at
                }
                
                export_data.append(export_record)
        
        print(f"   Export Data Count: {len(export_data)}")
        if export_data:
            print(f"   First Record: {json.dumps(export_data[0], indent=4)}")
            
            # Test JSONL format
            print("\n4. Testing JSONL Format:")
            jsonl_content = '\n'.join([json.dumps(record) for record in export_data])
            lines = jsonl_content.split('\n')
            print(f"   JSONL Lines: {len(lines)}")
            print(f"   First Line: {lines[0]}")
            if len(lines) > 1:
                print(f"   Second Line: {lines[1]}")
        
        db.close()
        
        print("\n" + "=" * 60)
        print("Export functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"   Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_export_functionality()