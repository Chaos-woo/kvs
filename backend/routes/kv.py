from flask import Blueprint, jsonify, request
import sys
from pathlib import Path
import traceback

# Add the parent directory to the Python path if it's not already there
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import using standard Python imports
from models import SessionLocal
from models.key_value import Key, Val, KVRelation, KVSearch
from models.key_value import create_kv_data, update_kv_data, delete_kv_data, search_kv_data
from utils.logger import api_logger, error_logger, log_exception
from services.clustering import KValueClusteringService

kv_bp = Blueprint('kv', __name__)

@kv_bp.route('/kv', methods=['POST'])
def create_kv():
    """Create a new KV entry with multiple values"""
    db = None
    try:
        # Log the incoming request
        api_logger.info(f"[DEBUG_LOG] POST /kv - Creating new KV entry")

        # Initialize database session
        try:
            db = SessionLocal()
            api_logger.info(f"[DEBUG_LOG] Database session created successfully")
        except Exception as e:
            log_exception(e, "Failed to create database session")
            return jsonify({
                "status": "error",
                "message": "Database connection failed"
            }), 500

        # Parse request data
        try:
            data = request.json
            api_logger.info(f"[DEBUG_LOG] Request data parsed: {data}")
        except Exception as e:
            log_exception(e, "Failed to parse JSON request data")
            return jsonify({
                "status": "error",
                "message": "Invalid JSON data"
            }), 400

        if data is None:
            api_logger.error(f"[DEBUG_LOG] Request data is None")
            return jsonify({
                "status": "error",
                "message": "Request body must contain JSON data"
            }), 400

        key_text = data.get('key')
        val_list = data.get('vals', [])

        api_logger.info(f"[DEBUG_LOG] Extracted key: '{key_text}', vals: {val_list}")

        # Validate input
        if not key_text:
            api_logger.warning(f"[DEBUG_LOG] Key is missing or empty")
            return jsonify({
                "status": "error",
                "message": "Key is required"
            }), 400

        if not val_list or not isinstance(val_list, list):
            api_logger.warning(f"[DEBUG_LOG] Vals is invalid: {val_list}")
            return jsonify({
                "status": "error",
                "message": "Vals must be a non-empty list"
            }), 400

        # Create KV data
        try:
            api_logger.info(f"[DEBUG_LOG] Calling create_kv_data with key='{key_text}', vals={val_list}")
            key = create_kv_data(db, key_text, val_list)
            api_logger.info(f"[DEBUG_LOG] create_kv_data completed successfully, key.id={key.id}")
        except Exception as e:
            log_exception(e, f"Failed to create KV data - key: '{key_text}', vals: {val_list}")
            db.rollback()
            return jsonify({
                "status": "error",
                "message": f"Failed to create KV entry: {str(e)}"
            }), 500

        # Commit the transaction
        try:
            api_logger.info(f"[DEBUG_LOG] Committing database transaction")
            db.commit()
            api_logger.info(f"[DEBUG_LOG] Database transaction committed successfully")
        except Exception as e:
            log_exception(e, "Failed to commit database transaction")
            db.rollback()
            return jsonify({
                "status": "error",
                "message": "Failed to save data to database"
            }), 500

        # Get the vals for the response
        try:
            api_logger.info(f"[DEBUG_LOG] Fetching relations for key.id={key.id}")
            relations = db.query(KVRelation).filter(KVRelation.key_id == key.id).all()
            val_ids = [relation.val_id for relation in relations]
            api_logger.info(f"[DEBUG_LOG] Found {len(relations)} relations, val_ids: {val_ids}")

            vals = db.query(Val).filter(Val.id.in_(val_ids)).all()
            api_logger.info(f"[DEBUG_LOG] Found {len(vals)} vals")
        except Exception as e:
            log_exception(e, f"Failed to fetch response data for key.id={key.id}")
            return jsonify({
                "status": "error",
                "message": "Data created but failed to fetch response"
            }), 500

        response_data = {
            "status": "success",
            "data": {
                "id": key.id,
                "key": key.key,
                "vals": [val.val for val in vals],
                "created_at": key.created_at.isoformat(),
                "updated_at": key.updated_at.isoformat() if key.updated_at else None
            }
        }

        api_logger.info(f"[DEBUG_LOG] POST /kv completed successfully, returning: {response_data}")
        return jsonify(response_data)

    except Exception as e:
        # Catch any unexpected exceptions
        log_exception(e, "Unexpected error in create_kv endpoint")
        if db:
            try:
                db.rollback()
            except:
                pass
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500
    finally:
        if db:
            try:
                db.close()
                api_logger.info(f"[DEBUG_LOG] Database session closed")
            except Exception as e:
                log_exception(e, "Failed to close database session")

@kv_bp.route('/kv/<int:key_id>', methods=['PUT'])
def update_kv(key_id):
    """Update an existing KV entry"""
    db = SessionLocal()
    try:
        data = request.json
        key_text = data.get('key')
        val_list = data.get('vals', [])

        if not key_text:
            return jsonify({
                "status": "error",
                "message": "Key is required"
            }), 400

        if not val_list or not isinstance(val_list, list):
            return jsonify({
                "status": "error",
                "message": "Vals must be a non-empty list"
            }), 400

        key = update_kv_data(db, key_id, key_text, val_list)

        # Commit the transaction
        db.commit()

        # Get the vals for the response
        relations = db.query(KVRelation).filter(KVRelation.key_id == key.id).all()
        val_ids = [relation.val_id for relation in relations]
        vals = db.query(Val).filter(Val.id.in_(val_ids)).all()

        return jsonify({
            "status": "success",
            "data": {
                "id": key.id,
                "key": key.key,
                "vals": [val.val for val in vals],
                "created_at": key.created_at.isoformat(),
                "updated_at": key.updated_at.isoformat() if key.updated_at else None
            }
        })
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
    except Exception as e:
        db.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        db.close()

@kv_bp.route('/kv/<int:key_id>', methods=['DELETE'])
def delete_kv(key_id):
    """Delete a KV entry by key ID"""
    db = SessionLocal()
    try:
        result = delete_kv_data(db, key_id)

        # Commit the transaction
        db.commit()

        return jsonify({
            "status": "success",
            "message": f"KV entry with ID {key_id} deleted successfully"
        })
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
    except Exception as e:
        db.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        db.close()

@kv_bp.route('/kv/batch-delete', methods=['DELETE'])
def batch_delete_kv():
    """Batch delete KV entries by key IDs"""
    db = SessionLocal()
    try:
        data = request.get_json()
        if not data or 'key_ids' not in data:
            return jsonify({
                "status": "error",
                "message": "key_ids array is required"
            }), 400
        
        key_ids = data['key_ids']
        if not isinstance(key_ids, list) or not key_ids:
            return jsonify({
                "status": "error",
                "message": "key_ids must be a non-empty array"
            }), 400
        
        deleted_count = 0
        failed_deletions = []
        
        for key_id in key_ids:
            try:
                delete_kv_data(db, key_id)
                deleted_count += 1
            except ValueError as e:
                failed_deletions.append({"key_id": key_id, "error": str(e)})
            except Exception as e:
                failed_deletions.append({"key_id": key_id, "error": str(e)})
        
        # Commit the transaction
        db.commit()
        
        response_data = {
            "status": "success",
            "message": f"Successfully deleted {deleted_count} KV entries",
            "deleted_count": deleted_count,
            "total_requested": len(key_ids)
        }
        
        if failed_deletions:
            response_data["failed_deletions"] = failed_deletions
        
        return jsonify(response_data)
        
    except Exception as e:
        db.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        db.close()

@kv_bp.route('/kv/search', methods=['GET'])
def search_kv():
    """Search KV data using FTS5"""
    db = SessionLocal()
    try:
        query = request.args.get('q', '')
        mode = request.args.get('mode', 'mixed')  # Default to mixed mode

        if not query:
            return jsonify({
                "status": "error",
                "message": "Search query is required"
            }), 400

        # Validate mode parameter
        if mode not in ['key', 'value', 'mixed']:
            mode = 'mixed'  # Default to mixed if invalid mode provided

        # Log the search query and mode for debugging
        print(f"Search query: {query}, mode: {mode}")

        keys = search_kv_data(db, query, mode)

        # Ensure keys is not None to prevent iteration error
        if keys is None:
            keys = []

        result = []
        for key in keys:
            try:
                # Get the vals for the response
                relations = db.query(KVRelation).filter(KVRelation.key_id == key.id).all()
                val_ids = [relation.val_id for relation in relations]
                vals = db.query(Val).filter(Val.id.in_(val_ids)).all()

                result.append({
                    "id": key.id,
                    "key": key.key,
                    "vals": [val.val for val in vals],
                    "created_at": key.created_at.isoformat(),
                    "updated_at": key.updated_at.isoformat() if key.updated_at else None
                })
            except Exception as e:
                print(f"Error processing key {key.id}: {str(e)}")
                # Continue with next key if there's an error with this one
                continue

        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        print(f"Error in search_kv endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        db.close()

@kv_bp.route('/kv', methods=['GET'])
def get_all_kvs():
    """Get all KV entries"""
    db = SessionLocal()
    try:
        keys = db.query(Key).all()

        result = []
        for key in keys:
            # Get the vals for the response
            relations = db.query(KVRelation).filter(KVRelation.key_id == key.id).all()
            val_ids = [relation.val_id for relation in relations]
            vals = db.query(Val).filter(Val.id.in_(val_ids)).all()

            result.append({
                "id": key.id,
                "key": key.key,
                "vals": [val.val for val in vals],
                "created_at": key.created_at.isoformat(),
                "updated_at": key.updated_at.isoformat() if key.updated_at else None
            })

        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        db.close()

@kv_bp.route('/kv/<int:key_id>', methods=['GET'])
def get_kv(key_id):
    """Get a KV entry by key ID"""
    db = SessionLocal()
    try:
        key = db.query(Key).filter(Key.id == key_id).first()

        if not key:
            return jsonify({
                "status": "error",
                "message": f"Key with ID {key_id} not found"
            }), 404

        # Get the vals for the response
        relations = db.query(KVRelation).filter(KVRelation.key_id == key.id).all()
        val_ids = [relation.val_id for relation in relations]
        vals = db.query(Val).filter(Val.id.in_(val_ids)).all()

        return jsonify({
            "status": "success",
            "data": {
                "id": key.id,
                "key": key.key,
                "vals": [val.val for val in vals],
                "created_at": key.created_at.isoformat(),
                "updated_at": key.updated_at.isoformat() if key.updated_at else None
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        db.close()

@kv_bp.route('/kv/stats', methods=['GET'])
def get_kv_stats():
    """Get KV statistics"""
    db = SessionLocal()
    try:
        api_logger.info("[DEBUG_LOG] get_kv_stats: Starting KV statistics calculation")

        # Count unique K values
        unique_k_count = db.query(Key).count()
        api_logger.info(f"[DEBUG_LOG] get_kv_stats: Unique K count = {unique_k_count}")

        # Count total V values
        total_v_count = db.query(Val).count()
        api_logger.info(f"[DEBUG_LOG] get_kv_stats: Total V count = {total_v_count}")

        # Count K values with different numbers of V values
        from sqlalchemy import func

        # Query to get the count of V values for each K
        k_v_counts = db.query(
            Key.id,
            Key.key,
            func.count(KVRelation.val_id).label('v_count')
        ).join(KVRelation, Key.id == KVRelation.key_id)\
         .group_by(Key.id, Key.key)\
         .all()

        api_logger.info(f"[DEBUG_LOG] get_kv_stats: Found {len(k_v_counts)} K entries with V relationships")

        # Initialize counters
        v_distribution = {
            '1': 0,  # K with 1 V
            '2': 0,  # K with 2 V
            '3': 0,  # K with 3 V
            '4': 0,  # K with 4 V
            '5': 0,  # K with 5 V
            '5+': 0  # K with 5+ V
        }

        # Count distribution
        for k_id, k_key, v_count in k_v_counts:
            if v_count == 1:
                v_distribution['1'] += 1
            elif v_count == 2:
                v_distribution['2'] += 1
            elif v_count == 3:
                v_distribution['3'] += 1
            elif v_count == 4:
                v_distribution['4'] += 1
            elif v_count == 5:
                v_distribution['5'] += 1
            elif v_count > 5:
                v_distribution['5+'] += 1

        api_logger.info(f"[DEBUG_LOG] get_kv_stats: V distribution = {v_distribution}")

        result = {
            "unique_k_count": unique_k_count,
            "total_v_count": total_v_count,
            "v_distribution": v_distribution
        }

        api_logger.info(f"[DEBUG_LOG] get_kv_stats: Final result = {result}")

        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        api_logger.error(f"[DEBUG_LOG] get_kv_stats: Error occurred - {str(e)}")
        log_exception(e, "Failed to get KV statistics")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        db.close()

@kv_bp.route('/kv/export/stats', methods=['GET'])
def get_export_stats():
    """Get statistics for KV data export"""
    db = SessionLocal()
    try:
        api_logger.info("[DEBUG_LOG] get_export_stats: Starting export statistics calculation")

        # Count unique K values
        unique_k_count = db.query(Key).count()
        api_logger.info(f"[DEBUG_LOG] get_export_stats: Unique K count = {unique_k_count}")

        # Count total V values
        total_v_count = db.query(Val).count()
        api_logger.info(f"[DEBUG_LOG] get_export_stats: Total V count = {total_v_count}")

        # Count KV pairs as unique keys from kv_relation (deduplicated)
        # This represents keys that have at least one relation
        unique_keys_with_relations = db.query(KVRelation.key_id).distinct().count()
        api_logger.info(f"[DEBUG_LOG] get_export_stats: Unique keys with relations = {unique_keys_with_relations}")
        
        # Count orphaned keys (keys without any relations)
        # These will be exported with empty value arrays
        orphaned_keys_count = db.query(Key).filter(
            ~Key.id.in_(db.query(KVRelation.key_id).distinct())
        ).count()
        api_logger.info(f"[DEBUG_LOG] get_export_stats: Orphaned keys count = {orphaned_keys_count}")
        
        # Total KV pairs = keys with relations + orphaned keys
        total_kv_pairs = unique_keys_with_relations + orphaned_keys_count
        api_logger.info(f"[DEBUG_LOG] get_export_stats: Total KV pairs (corrected) = {total_kv_pairs}")

        result = {
            "k_count": unique_k_count,
            "v_count": total_v_count,
            "kv_pairs_count": total_kv_pairs
        }

        api_logger.info(f"[DEBUG_LOG] get_export_stats: Final result = {result}")

        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        api_logger.error(f"[DEBUG_LOG] get_export_stats: Error occurred - {str(e)}")
        log_exception(e, "Failed to get export statistics")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        db.close()

@kv_bp.route('/kv/export', methods=['GET'])
def export_kv_data():
    """Export all KV data in JSONL format"""
    db = SessionLocal()
    try:
        api_logger.info("[DEBUG_LOG] export_kv_data: Starting KV data export")

        # Query all keys with their relationships and values
        from sqlalchemy import func
        
        # Get all keys with their associated values and creation timestamps
        # We need to group by key and collect all values for each key
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
            else:
                # Handle orphaned keys (keys without relations)
                # Export them with empty value arrays as mentioned in the issue
                api_logger.info(f"[DEBUG_LOG] export_kv_data: Found orphaned key '{key.key}' with no relations")
                
                # Use the key's creation timestamp for orphaned keys
                create_at = key.created_at.isoformat()
                
                # Create the export record with empty value array
                export_record = {
                    "k": key.key,
                    "v": [],  # Empty array for orphaned keys
                    "create_at": create_at
                }
                
                export_data.append(export_record)
        
        api_logger.info(f"[DEBUG_LOG] export_kv_data: Exported {len(export_data)} KV records")

        return jsonify({
            "status": "success",
            "data": export_data,
            "count": len(export_data)
        })
    except Exception as e:
        api_logger.error(f"[DEBUG_LOG] export_kv_data: Error occurred - {str(e)}")
        log_exception(e, "Failed to export KV data")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        db.close()

@kv_bp.route('/kv/import', methods=['POST'])
def import_kv_data():
    """Import KV data from JSONL format"""
    db = None
    try:
        api_logger.info("[DEBUG_LOG] POST /kv/import - Starting KV data import")

        # Initialize database session
        try:
            db = SessionLocal()
            api_logger.info("[DEBUG_LOG] Database session created successfully")
        except Exception as e:
            log_exception(e, "Failed to create database session")
            return jsonify({
                "status": "error",
                "message": "Database connection failed"
            }), 500

        # Parse request data
        try:
            data = request.json
            api_logger.info(f"[DEBUG_LOG] Request data parsed: {data}")
        except Exception as e:
            log_exception(e, "Failed to parse JSON request data")
            return jsonify({
                "status": "error",
                "message": "Invalid JSON data"
            }), 400

        if data is None:
            api_logger.error("[DEBUG_LOG] Request data is None")
            return jsonify({
                "status": "error",
                "message": "Request body must contain JSON data"
            }), 400

        import_data = data.get('data', [])
        api_logger.info(f"[DEBUG_LOG] Import data contains {len(import_data)} items")

        # Validate input
        if not import_data or not isinstance(import_data, list):
            api_logger.warning("[DEBUG_LOG] Import data is invalid or empty")
            return jsonify({
                "status": "error",
                "message": "Data must be a non-empty list"
            }), 400

        # Process import data
        imported_count = 0
        failed_count = 0
        failed_items = []

        for index, item in enumerate(import_data):
            try:
                api_logger.info(f"[DEBUG_LOG] Processing item {index + 1}/{len(import_data)}: {item}")

                # Validate item structure
                if not isinstance(item, dict):
                    raise ValueError("Item must be a dictionary")

                k = item.get('k')
                v = item.get('v')
                create_at = item.get('create_at')

                # Validate required fields
                if not k or not isinstance(k, str):
                    raise ValueError("Field 'k' is required and must be a string")
                
                if not v or not isinstance(v, list) or len(v) == 0:
                    raise ValueError("Field 'v' is required and must be a non-empty list")
                
                if not all(isinstance(val, str) for val in v):
                    raise ValueError("All values in 'v' must be strings")
                
                if not create_at or not isinstance(create_at, str):
                    raise ValueError("Field 'create_at' is required and must be a string")

                # Validate timestamp format
                try:
                    from datetime import datetime
                    datetime.fromisoformat(create_at.replace('Z', '+00:00'))
                except ValueError:
                    raise ValueError("Field 'create_at' has invalid timestamp format")

                # Create KV data using existing helper function
                api_logger.info(f"[DEBUG_LOG] Creating KV data for key='{k}', vals={v}")
                key = create_kv_data(db, k, v)
                api_logger.info(f"[DEBUG_LOG] KV data created successfully with key.id={key.id}")
                
                imported_count += 1

            except Exception as e:
                api_logger.error(f"[DEBUG_LOG] Failed to process item {index + 1}: {str(e)}")
                failed_count += 1
                failed_items.append({
                    "index": index,
                    "error": str(e)
                })
                # Continue processing other items instead of failing completely
                continue

        # Commit the transaction if any items were imported successfully
        if imported_count > 0:
            try:
                api_logger.info("[DEBUG_LOG] Committing database transaction")
                db.commit()
                api_logger.info("[DEBUG_LOG] Database transaction committed successfully")
            except Exception as e:
                log_exception(e, "Failed to commit database transaction")
                db.rollback()
                return jsonify({
                    "status": "error",
                    "message": "Failed to save data to database"
                }), 500
        else:
            # No items were imported successfully
            api_logger.info("[DEBUG_LOG] No items imported successfully, rolling back transaction")
            db.rollback()

        # Prepare response
        response_data = {
            "imported_count": imported_count,
            "failed_count": failed_count,
            "total_count": len(import_data),
            "failed_items": failed_items
        }

        api_logger.info(f"[DEBUG_LOG] Import completed: {response_data}")

        return jsonify({
            "status": "success",
            "data": response_data
        })

    except Exception as e:
        api_logger.error(f"[DEBUG_LOG] import_kv_data: Unexpected error - {str(e)}")
        log_exception(e, "Failed to import KV data")
        if db:
            db.rollback()
        return jsonify({
            "status": "error",
            "message": f"Import failed: {str(e)}"
        }), 500
    finally:
        if db:
            db.close()


@kv_bp.route('/kv/cluster', methods=['GET'])
def cluster_keys():
    """
    K值聚类API端点
    支持多种聚类算法和参数配置
    """
    db = None
    try:
        api_logger.info("[DEBUG_LOG] cluster_keys: Starting K-value clustering")
        
        # 获取请求参数
        algorithm = request.args.get('algorithm', 'hybrid')  # hybrid, similarity, pattern
        similarity_threshold = float(request.args.get('similarity_threshold', 0.6))
        min_cluster_size = int(request.args.get('min_cluster_size', 2))
        
        api_logger.info(f"[DEBUG_LOG] Clustering parameters: algorithm={algorithm}, "
                       f"similarity_threshold={similarity_threshold}, min_cluster_size={min_cluster_size}")
        
        # 验证参数
        if algorithm not in ['hybrid', 'similarity', 'pattern']:
            return jsonify({
                "status": "error",
                "message": "Invalid algorithm. Must be one of: hybrid, similarity, pattern"
            }), 400
        
        if not (0.0 <= similarity_threshold <= 1.0):
            return jsonify({
                "status": "error",
                "message": "similarity_threshold must be between 0.0 and 1.0"
            }), 400
        
        if min_cluster_size < 1:
            return jsonify({
                "status": "error",
                "message": "min_cluster_size must be at least 1"
            }), 400
        
        # 获取数据库连接
        db = SessionLocal()
        
        # 获取所有唯一的K值
        api_logger.info("[DEBUG_LOG] Fetching all unique keys from database")
        keys_query = db.query(Key.key).distinct().all()
        keys = [key.key for key in keys_query]
        
        api_logger.info(f"[DEBUG_LOG] Found {len(keys)} unique keys for clustering")
        
        if len(keys) == 0:
            return jsonify({
                "status": "success",
                "data": {
                    "clusters": [],
                    "total_keys": 0,
                    "total_clusters": 0,
                    "algorithm": algorithm,
                    "parameters": {
                        "similarity_threshold": similarity_threshold,
                        "min_cluster_size": min_cluster_size
                    }
                }
            })
        
        # 创建聚类服务实例
        clustering_service = KValueClusteringService(
            similarity_threshold=similarity_threshold,
            min_cluster_size=min_cluster_size
        )
        
        # 执行聚类
        api_logger.info(f"[DEBUG_LOG] Starting clustering with algorithm: {algorithm}")
        clustering_result = clustering_service.cluster_keys(keys, algorithm=algorithm)
        
        api_logger.info(f"[DEBUG_LOG] Clustering completed. Found {clustering_result['total_clusters']} clusters")
        
        return jsonify({
            "status": "success",
            "data": clustering_result
        })
        
    except ValueError as e:
        api_logger.error(f"[DEBUG_LOG] cluster_keys: Parameter validation error - {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
        
    except Exception as e:
        api_logger.error(f"[DEBUG_LOG] cluster_keys: Unexpected error - {str(e)}")
        log_exception(e, "Failed to cluster K values")
        return jsonify({
            "status": "error",
            "message": f"Clustering failed: {str(e)}"
        }), 500
        
    finally:
        if db:
            db.close()
