from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sys
from pathlib import Path

# Import Base and engine from models/__init__.py using standard import
from . import Base, engine

# Key table
class Key(Base):
    """Model for storing Key data"""
    __tablename__ = 'keys'

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with Val through KVRelation
    vals = relationship("KVRelation", back_populates="key", cascade="all, delete-orphan")

# Val table
class Val(Base):
    """Model for storing Val data"""
    __tablename__ = 'vals'

    id = Column(Integer, primary_key=True, index=True)
    val = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship with Key through KVRelation
    keys = relationship("KVRelation", back_populates="val", cascade="all, delete-orphan")

# KV relationship table
class KVRelation(Base):
    """Model for storing Key-Val relationships"""
    __tablename__ = 'kv_relations'

    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(Integer, ForeignKey('keys.id', ondelete='CASCADE'), nullable=False)
    val_id = Column(Integer, ForeignKey('vals.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    key = relationship("Key", back_populates="vals")
    val = relationship("Val", back_populates="keys")

# FTS5 virtual table for full-text search
class KVSearch:
    """Virtual table for full-text search of KV data"""
    __tablename__ = 'kv_search'

    # FTS5 requires rowid as primary key
    rowid = None
    key = None
    key_id = None
    full_content = None

    def __init__(self, key=None, key_id=None, full_content=None, rowid=None):
        self.key = key
        self.key_id = key_id
        self.full_content = full_content
        self.rowid = rowid

    # Note: The actual FTS5 virtual table is created by the create_fts5_table() function below

# Enable foreign keys
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Create FTS5 virtual table manually if it doesn't exist
def create_fts5_table():
    from sqlalchemy import text
    conn = engine.connect()
    trans = conn.begin()

    try:
        # Then create the FTS5 virtual table
        conn.execute(text("""
        CREATE VIRTUAL TABLE IF NOT EXISTS kv_search USING fts5(
            key, 
            key_id, 
            full_content, 
            tokenize='porter'
        )
        """))
        trans.commit()
    except Exception as e:
        trans.rollback()
        print(f"Error creating FTS5 table: {e}")
        raise
    finally:
        conn.close()

# Don't automatically create the FTS5 table when the module is imported
# This will be handled by the application startup code

# Helper functions for KV operations
def create_kv_data(db_session, key_text, val_list):
    """Create a new KV entry with multiple values"""
    # Import logger here to avoid circular imports
    import sys
    from pathlib import Path
    backend_dir = Path(__file__).resolve().parent.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    from utils.logger import api_logger, log_exception

    try:
        api_logger.info(f"[DEBUG_LOG] create_kv_data: Starting with key='{key_text}', vals={val_list}")

        # Create Key
        try:
            api_logger.info(f"[DEBUG_LOG] create_kv_data: Creating Key object")
            key = Key(key=key_text)
            db_session.add(key)
            api_logger.info(f"[DEBUG_LOG] create_kv_data: Key added to session, flushing to get ID")
            db_session.flush()  # Flush to get the key ID
            api_logger.info(f"[DEBUG_LOG] create_kv_data: Key created successfully with ID={key.id}")
        except Exception as e:
            log_exception(e, f"Failed to create Key with text='{key_text}'")
            raise Exception(f"Failed to create key: {str(e)}")

        # Create Vals and KVRelations
        val_texts = []
        try:
            api_logger.info(f"[DEBUG_LOG] create_kv_data: Creating {len(val_list)} Val objects")
            for i, val_text in enumerate(val_list):
                api_logger.info(f"[DEBUG_LOG] create_kv_data: Creating Val {i+1}/{len(val_list)}: '{val_text}'")

                # Create Val
                val = Val(val=val_text)
                db_session.add(val)
                db_session.flush()  # Flush to get the val ID
                api_logger.info(f"[DEBUG_LOG] create_kv_data: Val created with ID={val.id}")

                # Create relation
                relation = KVRelation(key_id=key.id, val_id=val.id)
                db_session.add(relation)
                api_logger.info(f"[DEBUG_LOG] create_kv_data: KVRelation created (key_id={key.id}, val_id={val.id})")

                val_texts.append(val_text)

            api_logger.info(f"[DEBUG_LOG] create_kv_data: All Vals and KVRelations created successfully")
        except Exception as e:
            log_exception(e, f"Failed to create Vals/KVRelations for key_id={key.id}, val_list={val_list}")
            raise Exception(f"Failed to create values: {str(e)}")

        # Create FTS entry
        try:
            full_content = "\n".join(val_texts)
            api_logger.info(f"[DEBUG_LOG] create_kv_data: Creating FTS entry with full_content length={len(full_content)}")

            # Insert directly into the FTS5 virtual table
            from sqlalchemy import text
            fts_query = text("""
            INSERT INTO kv_search (key, key_id, full_content)
            VALUES (:key, :key_id, :full_content)
            """)
            fts_params = {"key": key_text, "key_id": key.id, "full_content": full_content}

            api_logger.info(f"[DEBUG_LOG] create_kv_data: Executing FTS insert with params: {fts_params}")
            db_session.execute(fts_query, fts_params)
            api_logger.info(f"[DEBUG_LOG] create_kv_data: FTS entry created successfully")
        except Exception as e:
            log_exception(e, f"Failed to create FTS entry for key_id={key.id}, key='{key_text}', full_content='{full_content}'")
            raise Exception(f"Failed to create search index: {str(e)}")

        api_logger.info(f"[DEBUG_LOG] create_kv_data: Completed successfully, returning key with ID={key.id}")
        # Don't commit here - let the caller handle the transaction
        return key
    except Exception as e:
        # Log the exception with context and re-raise
        log_exception(e, f"create_kv_data failed - key: '{key_text}', vals: {val_list}")
        raise

def update_kv_data(db_session, key_id, key_text, val_list):
    """Update an existing KV entry"""
    try:
        # Get the key
        key = db_session.query(Key).filter(Key.id == key_id).first()
        if not key:
            raise ValueError(f"Key with ID {key_id} not found")

        # Update key text
        key.key = key_text

        # Delete existing relations and vals
        relations = db_session.query(KVRelation).filter(KVRelation.key_id == key_id).all()
        val_ids = [relation.val_id for relation in relations]

        # Delete relations
        for relation in relations:
            db_session.delete(relation)

        # Delete vals
        for val_id in val_ids:
            val = db_session.query(Val).filter(Val.id == val_id).first()
            if val:
                db_session.delete(val)

        # Delete FTS entry
        from sqlalchemy import text
        db_session.execute(text("""
        DELETE FROM kv_search WHERE key_id = :key_id
        """), {"key_id": key_id})

        # Create new vals and relations
        val_texts = []
        for val_text in val_list:
            val = Val(val=val_text)
            db_session.add(val)
            db_session.flush()  # Flush to get the val ID

            # Create relation
            relation = KVRelation(key_id=key.id, val_id=val.id)
            db_session.add(relation)

            val_texts.append(val_text)

        # Create new FTS entry
        full_content = "\n".join(val_texts)
        # Insert directly into the FTS5 virtual table
        from sqlalchemy import text
        db_session.execute(text("""
        INSERT INTO kv_search (key, key_id, full_content)
        VALUES (:key, :key_id, :full_content)
        """), {"key": key_text, "key_id": key.id, "full_content": full_content})

        # Don't commit here - let the caller handle the transaction
        return key
    except Exception as e:
        # Re-raise the exception to let the caller handle it
        raise

def delete_kv_data(db_session, key_id):
    """Delete a KV entry by key ID"""
    try:
        # Get the key
        key = db_session.query(Key).filter(Key.id == key_id).first()
        if not key:
            raise ValueError(f"Key with ID {key_id} not found")

        # Delete FTS entry
        from sqlalchemy import text
        db_session.execute(text("""
        DELETE FROM kv_search WHERE key_id = :key_id
        """), {"key_id": key_id})

        # Get and delete relations and vals
        relations = db_session.query(KVRelation).filter(KVRelation.key_id == key_id).all()
        val_ids = [relation.val_id for relation in relations]

        # Delete relations
        for relation in relations:
            db_session.delete(relation)

        # Delete vals
        for val_id in val_ids:
            val = db_session.query(Val).filter(Val.id == val_id).first()
            if val:
                db_session.delete(val)

        # Delete key
        db_session.delete(key)

        # Don't commit here - let the caller handle the transaction
        return True
    except Exception as e:
        # Re-raise the exception to let the caller handle it
        raise

def search_kv_data(db_session, query, mode="mixed"):
    """Search KV data using FTS5 prefix matching
    
    Args:
        db_session: Database session
        query: Search query string
        mode: Search mode - 'key', 'value', or 'mixed' (default)
    """
    try:
        # Use a raw SQL query with the correct FTS5 syntax
        from sqlalchemy import text

        # Execute a direct SQL query to use FTS5's prefix matching
        # This uses the SQLite FTS5 syntax directly
        conn = db_session.connection().connection  # Get the underlying SQLite connection
        cursor = conn.cursor()

        # Add wildcard for prefix matching
        query_with_wildcard = query + "*"

        matching_key_ids = []

        if mode == "key":
            # Search only in the key column
            cursor.execute(
                "SELECT key_id FROM kv_search WHERE kv_search MATCH ?",
                (f"key:{query_with_wildcard}",)
            )
            matching_key_ids = [row[0] for row in cursor.fetchall()]
        elif mode == "value":
            # Search only in the full_content column
            cursor.execute(
                "SELECT key_id FROM kv_search WHERE kv_search MATCH ?",
                (f"full_content:{query_with_wildcard}",)
            )
            matching_key_ids = [row[0] for row in cursor.fetchall()]
        else:  # mode == "mixed" or any other value (default behavior)
            # Search in both key and full_content columns
            cursor.execute(
                "SELECT key_id FROM kv_search WHERE kv_search MATCH ?",
                (f"key:{query_with_wildcard}",)
            )
            key_matches = [row[0] for row in cursor.fetchall()]

            cursor.execute(
                "SELECT key_id FROM kv_search WHERE kv_search MATCH ?",
                (f"full_content:{query_with_wildcard}",)
            )
            content_matches = [row[0] for row in cursor.fetchall()]

            # Combine the results and deduplicate based on key_id
            matching_key_ids = list(set(key_matches + content_matches))

        # Get the corresponding keys
        if matching_key_ids:
            # Query the keys and create a dictionary with key.id as the key to ensure uniqueness
            keys_dict = {}
            keys = db_session.query(Key).filter(Key.id.in_(matching_key_ids)).all()
            for key in keys:
                keys_dict[key.id] = key

            # Return the values of the dictionary (unique keys)
            return list(keys_dict.values())

        return []
    except Exception as e:
        # Log the error for debugging
        print(f"Error in search_kv_data: {str(e)}")
        return []
