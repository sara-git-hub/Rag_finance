from fastapi import APIRouter, Depends, Request, Query, status
from fastapi.responses import JSONResponse
from typing import Optional
from helpers.auth import require_admin
from models.ProjectModel import ProjectModel
from models.AssetModel import AssetModel
from models.ChunkModel import ChunkModel
from models.ConversationModel import ConversationModel
from models.enums.AssetTypeEnum import AssetTypeEnum
from sqlalchemy.future import select
from sqlalchemy import func, delete
from models.db_schemes import Project, Asset, DataChunk, Conversation, Message
import logging

logger = logging.getLogger('uvicorn.error')

admin_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["api_v1", "admin"],
)

# ==================== PROJECTS ====================

@admin_router.get("/projects")
async def get_all_projects(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_admin)
):
    """Get all projects with pagination"""
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    projects, total_pages = await project_model.get_all_projects(
        page=page,
        page_size=page_size
    )

    # Get file count for each project
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )

    projects_data = []
    for project in projects:
        files = await asset_model.get_all_project_assets(
            asset_project_id=project.project_id,
            asset_type=AssetTypeEnum.FILE.value
        )
        projects_data.append({
            "project_id": project.project_id,
            "project_uuid": str(project.project_uuid),
            "project_name": project.project_name,
            "project_language": project.project_language,
            "file_count": len(files),
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
        })

    return JSONResponse(
        content={
            "signal": "PROJECTS_RETRIEVED",
            "projects": projects_data,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )

@admin_router.get("/projects/{project_id}")
async def get_project(
    request: Request,
    project_id: int,
    current_user: dict = Depends(require_admin)
):
    """Get a single project by ID"""
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    return JSONResponse(
        content={
            "signal": "PROJECT_RETRIEVED",
            "project": {
                "project_id": project.project_id,
                "project_uuid": str(project.project_uuid),
                "project_name": project.project_name,
                "project_language": project.project_language,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            }
        }
    )

@admin_router.delete("/projects/{project_id}")
async def delete_project(
    request: Request,
    project_id: int,
    current_user: dict = Depends(require_admin)
):
    """Delete a project and all its related data"""
    async with request.app.db_client() as session:
        async with session.begin():
            # Delete related chunks
            await session.execute(
                delete(DataChunk).where(DataChunk.chunk_project_id == project_id)
            )

            # Delete related assets
            await session.execute(
                delete(Asset).where(Asset.asset_project_id == project_id)
            )

            # Delete project
            result = await session.execute(
                delete(Project).where(Project.project_id == project_id)
            )

            if result.rowcount == 0:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"signal": "PROJECT_NOT_FOUND"}
                )

    return JSONResponse(
        content={"signal": "PROJECT_DELETED", "project_id": project_id}
    )

@admin_router.patch("/projects/{project_id}/name")
async def update_project_name(
    request: Request,
    project_id: int,
    current_user: dict = Depends(require_admin)
):
    """Update the name of a project"""
    body = await request.json()
    project_name = body.get("project_name")

    if not project_name:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": "PROJECT_NAME_REQUIRED"}
        )

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.update_project_name(
        project_id=project_id,
        name=project_name
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": "PROJECT_NOT_FOUND"}
        )

    return JSONResponse(
        content={
            "signal": "PROJECT_NAME_UPDATED",
            "project_id": project.project_id,
            "project_name": project.project_name
        }
    )

# ==================== ASSETS ====================

@admin_router.get("/assets")
async def get_all_assets(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[int] = Query(None),
    asset_type: Optional[str] = Query(None),
    current_user: dict = Depends(require_admin)
):
    """Get all assets with pagination and filters"""
    async with request.app.db_client() as session:
        # Build query
        query = select(Asset)

        if project_id:
            query = query.where(Asset.asset_project_id == project_id)

        if asset_type:
            query = query.where(Asset.asset_type == asset_type)

        # Get total count
        count_query = select(func.count(Asset.asset_id))
        if project_id:
            count_query = count_query.where(Asset.asset_project_id == project_id)
        if asset_type:
            count_query = count_query.where(Asset.asset_type == asset_type)

        total_result = await session.execute(count_query)
        total_count = total_result.scalar_one()
        total_pages = (total_count + page_size - 1) // page_size

        # Get paginated results
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(query)
        assets = result.scalars().all()

        assets_data = [
            {
                "asset_id": asset.asset_id,
                "asset_uuid": str(asset.asset_uuid),
                "asset_type": asset.asset_type,
                "asset_name": asset.asset_name,
                "asset_size": asset.asset_size,
                "asset_project_id": asset.asset_project_id,
                "project_id": asset.asset_project_id,  # Alias for frontend
                "created_at": asset.created_at.isoformat() if asset.created_at else None,
                "updated_at": asset.updated_at.isoformat() if asset.updated_at else None,
            }
            for asset in assets
        ]

    return JSONResponse(
        content={
            "signal": "ASSETS_RETRIEVED",
            "assets": assets_data,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_count": total_count
        }
    )

@admin_router.delete("/assets/{asset_id}")
async def delete_asset(
    request: Request,
    asset_id: int,
    current_user: dict = Depends(require_admin)
):
    """Delete an asset, its related chunks, and vectors"""
    async with request.app.db_client() as session:
        async with session.begin():
            # First, get the asset to find its project_id
            asset_query = select(Asset).where(Asset.asset_id == asset_id)
            asset_result = await session.execute(asset_query)
            asset = asset_result.scalar_one_or_none()

            if not asset:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"signal": "ASSET_NOT_FOUND"}
                )

            project_id = asset.asset_project_id

            # Get all chunk IDs for this asset (needed to delete vectors)
            chunk_ids_query = select(DataChunk.chunk_id).where(DataChunk.chunk_asset_id == asset_id)
            chunk_ids_result = await session.execute(chunk_ids_query)
            chunk_ids = [row[0] for row in chunk_ids_result]
            # Delete related chunks from database
            await session.execute(
                delete(DataChunk).where(DataChunk.chunk_asset_id == asset_id)
            )

            # Delete asset
            result = await session.execute(
                delete(Asset).where(Asset.asset_id == asset_id)
            )

    # Delete vectors from Qdrant (outside of DB transaction)
    if chunk_ids:
        try:
            from models.ProjectModel import ProjectModel
            from controllers.NLPController import NLPController

            project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
            project = await project_model.get_project_or_create_one(project_id=project_id)

            nlp_controller = NLPController(
                embeddings_service=request.app.embeddings_service,
                generation_backend=request.app.generation_backend,
                generation_model=request.app.generation_model,
                api_key=request.app.generation_api_key,
                vector_db_backend=request.app.vector_db_backend,
                vector_db_path=request.app.vector_db_path,
                connection_string=request.app.postgres_conn_sync,
                qdrant_url=request.app.qdrant_url,
                max_tokens=request.app.generation_max_tokens,
                temperature=request.app.generation_temperature
            )

            await nlp_controller.delete_vectors_by_chunk_ids(project=project, chunk_ids=chunk_ids)
            logger.info(f"Deleted {len(chunk_ids)} vectors from Qdrant for asset {asset_id}")
        except Exception as e:
            logger.error(f"Error deleting vectors for asset {asset_id}: {e}")
            # Continue anyway - chunks and asset are already deleted

    return JSONResponse(
        content={"signal": "ASSET_DELETED", "asset_id": asset_id}
    )

# ==================== CHUNKS ====================

@admin_router.get("/chunks")
async def get_all_chunks(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[int] = Query(None),
    asset_id: Optional[int] = Query(None),
    current_user: dict = Depends(require_admin)
):
    """Get all chunks with pagination and filters"""
    async with request.app.db_client() as session:
        # Build query
        query = select(DataChunk)

        if project_id:
            query = query.where(DataChunk.chunk_project_id == project_id)

        if asset_id:
            query = query.where(DataChunk.chunk_asset_id == asset_id)

        # Get total count
        count_query = select(func.count(DataChunk.chunk_id))
        if project_id:
            count_query = count_query.where(DataChunk.chunk_project_id == project_id)
        if asset_id:
            count_query = count_query.where(DataChunk.chunk_asset_id == asset_id)

        total_result = await session.execute(count_query)
        total_count = total_result.scalar_one()
        total_pages = (total_count + page_size - 1) // page_size

        # Get paginated results
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(query)
        chunks = result.scalars().all()

        chunks_data = [
            {
                "chunk_id": chunk.chunk_id,
                "chunk_uuid": str(chunk.chunk_uuid),
                "chunk_text": chunk.chunk_text[:200] + "..." if len(chunk.chunk_text) > 200 else chunk.chunk_text,
                "chunk_order": chunk.chunk_order,
                "chunk_index": chunk.chunk_order,  # Alias for frontend
                "chunk_project_id": chunk.chunk_project_id,
                "project_id": chunk.chunk_project_id,  # Alias for frontend
                "chunk_asset_id": chunk.chunk_asset_id,
                "asset_id": chunk.chunk_asset_id,  # Alias for frontend
                "created_at": chunk.created_at.isoformat() if chunk.created_at else None,
            }
            for chunk in chunks
        ]

    return JSONResponse(
        content={
            "signal": "CHUNKS_RETRIEVED",
            "chunks": chunks_data,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_count": total_count
        }
    )

@admin_router.delete("/chunks/{chunk_id}")
async def delete_chunk(
    request: Request,
    chunk_id: int,
    current_user: dict = Depends(require_admin)
):
    """Delete a chunk"""
    async with request.app.db_client() as session:
        async with session.begin():
            result = await session.execute(
                delete(DataChunk).where(DataChunk.chunk_id == chunk_id)
            )

            if result.rowcount == 0:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"signal": "CHUNK_NOT_FOUND"}
                )

    return JSONResponse(
        content={"signal": "CHUNK_DELETED", "chunk_id": chunk_id}
    )

# ==================== CONVERSATIONS ====================

@admin_router.get("/conversations")
async def get_all_conversations(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    current_user: dict = Depends(require_admin)
):
    """Get all conversations with pagination and filters"""
    async with request.app.db_client() as session:
        # Build query
        query = select(Conversation)

        if project_id:
            query = query.where(Conversation.project_id == project_id)

        if user_id:
            query = query.where(Conversation.user_id == user_id)

        # Get total count
        count_query = select(func.count(Conversation.conversation_id))
        if project_id:
            count_query = count_query.where(Conversation.project_id == project_id)
        if user_id:
            count_query = count_query.where(Conversation.user_id == user_id)

        total_result = await session.execute(count_query)
        total_count = total_result.scalar_one()
        total_pages = (total_count + page_size - 1) // page_size

        # Get paginated results
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(query)
        conversations = result.scalars().all()

        # Get message counts for all conversations
        conversation_ids = [conv.conversation_id for conv in conversations]
        message_count_query = select(
            Message.conversation_id,
            func.count(Message.message_id).label('count')
        ).where(
            Message.conversation_id.in_(conversation_ids)
        ).group_by(Message.conversation_id)

        message_count_result = await session.execute(message_count_query)
        message_counts = {row[0]: row[1] for row in message_count_result}

        conversations_data = [
            {
                "conversation_id": conv.conversation_id,
                "conversation_uuid": str(conv.conversation_uuid),
                "title": conv.title,
                "status": conv.status,
                "user_id": conv.user_id,
                "project_id": conv.project_id,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                "message_count": message_counts.get(conv.conversation_id, 0),
            }
            for conv in conversations
        ]

    return JSONResponse(
        content={
            "signal": "CONVERSATIONS_RETRIEVED",
            "conversations": conversations_data,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_count": total_count
        }
    )

@admin_router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    request: Request,
    conversation_id: int,
    current_user: dict = Depends(require_admin)
):
    """Delete a conversation and its messages"""
    async with request.app.db_client() as session:
        async with session.begin():
            # Delete related messages
            await session.execute(
                delete(Message).where(Message.conversation_id == conversation_id)
            )

            # Delete conversation
            result = await session.execute(
                delete(Conversation).where(Conversation.conversation_id == conversation_id)
            )

            if result.rowcount == 0:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"signal": "CONVERSATION_NOT_FOUND"}
                )

    return JSONResponse(
        content={"signal": "CONVERSATION_DELETED", "conversation_id": conversation_id}
    )

# ==================== MESSAGES ====================

@admin_router.get("/messages")
async def get_all_messages(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    conversation_id: Optional[int] = Query(None),
    current_user: dict = Depends(require_admin)
):
    """Get all messages with pagination and filters"""
    async with request.app.db_client() as session:
        # Build query
        query = select(Message)

        if conversation_id:
            query = query.where(Message.conversation_id == conversation_id)

        # Get total count
        count_query = select(func.count(Message.message_id))
        if conversation_id:
            count_query = count_query.where(Message.conversation_id == conversation_id)

        total_result = await session.execute(count_query)
        total_count = total_result.scalar_one()
        total_pages = (total_count + page_size - 1) // page_size

        # Get paginated results
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(query)
        messages = result.scalars().all()

        messages_data = [
            {
                "message_id": msg.message_id,
                "conversation_id": msg.conversation_id,
                "role": msg.role,
                "content": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            }
            for msg in messages
        ]

    return JSONResponse(
        content={
            "signal": "MESSAGES_RETRIEVED",
            "messages": messages_data,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_count": total_count
        }
    )

@admin_router.delete("/messages/{message_id}")
async def delete_message(
    request: Request,
    message_id: int,
    current_user: dict = Depends(require_admin)
):
    """Delete a message"""
    async with request.app.db_client() as session:
        async with session.begin():
            result = await session.execute(
                delete(Message).where(Message.message_id == message_id)
            )

            if result.rowcount == 0:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"signal": "MESSAGE_NOT_FOUND"}
                )

    return JSONResponse(
        content={"signal": "MESSAGE_DELETED", "message_id": message_id}
    )

# ==================== VECTOR COLLECTIONS (QDRANT) ====================

@admin_router.get("/vectors/collections")
async def get_vector_collections(
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """Get all vector collections from Qdrant"""
    try:
        from qdrant_client import QdrantClient

        # Use Qdrant URL from app settings
        qdrant_url = getattr(request.app, 'qdrant_url', None)
        if qdrant_url:
            client = QdrantClient(url=qdrant_url)
        else:
            vector_db_path = getattr(request.app, 'vector_db_path', 'assets/database')
            client = QdrantClient(path=vector_db_path)

        collections = client.get_collections().collections
        collections_data = []

        for collection in collections:
            collection_info = client.get_collection(collection.name)

            # Extract vector configuration
            vectors_config = collection_info.config.params.vectors
            # Handle both named and unnamed vector configs
            if hasattr(vectors_config, 'size'):
                # Unnamed vector config
                vector_size = vectors_config.size
                vector_distance = vectors_config.distance.name if hasattr(vectors_config.distance, 'name') else str(vectors_config.distance)
            else:
                # Named vector configs (dict-like)
                # Get the first vector config if multiple exist
                first_vector = next(iter(vectors_config.values())) if vectors_config else None
                vector_size = first_vector.size if first_vector else None
                vector_distance = first_vector.distance.name if (first_vector and hasattr(first_vector.distance, 'name')) else None

            collections_data.append({
                "name": collection.name,
                "vectors_count": collection_info.points_count,
                "status": collection_info.status.value if hasattr(collection_info.status, 'value') else str(collection_info.status),
                "config": {
                    "params": {
                        "vectors": {
                            "size": vector_size,
                            "distance": vector_distance
                        }
                    }
                }
            })

        return JSONResponse(
            content={
                "signal": "COLLECTIONS_RETRIEVED",
                "collections": collections_data,
                "total_collections": len(collections_data)
            }
        )

    except Exception as e:
        logger.error(f"Error fetching collections: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": "ERROR_FETCHING_COLLECTIONS", "error": str(e)}
        )

@admin_router.get("/vectors/collections/{collection_name}")
async def get_collection_vectors(
    request: Request,
    collection_name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_admin)
):
    """Get vectors from a specific Qdrant collection with pagination"""
    try:
        from qdrant_client import QdrantClient

        qdrant_url = getattr(request.app, 'qdrant_url', None)
        if qdrant_url:
            client = QdrantClient(url=qdrant_url)
        else:
            vector_db_path = getattr(request.app, 'vector_db_path', 'assets/database')
            client = QdrantClient(path=vector_db_path)

        # Get collection info for total count
        collection_info = client.get_collection(collection_name)
        total_count = collection_info.points_count
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

        # Scroll through points with pagination
        offset = (page - 1) * page_size
        points, _ = client.scroll(
            collection_name=collection_name,
            limit=page_size,
            offset=offset,
            with_vectors=False,  # Don't include vectors (too large to display)
            with_payload=True
        )

        vectors_data = []
        for point in points:
            vectors_data.append({
                "id": str(point.id),
                "payload": point.payload,
            })

        return JSONResponse(
            content={
                "signal": "VECTORS_RETRIEVED",
                "collection_name": collection_name,
                "vectors": vectors_data,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "total_count": total_count
            }
        )

    except Exception as e:
        logger.error(f"Error fetching vectors: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": "ERROR_FETCHING_VECTORS", "error": str(e)}
        )

@admin_router.delete("/vectors/collections/{collection_name}")
async def delete_collection(
    request: Request,
    collection_name: str,
    current_user: dict = Depends(require_admin)
):
    """Delete a Qdrant vector collection"""
    try:
        from qdrant_client import QdrantClient

        qdrant_url = getattr(request.app, 'qdrant_url', None)
        if qdrant_url:
            client = QdrantClient(url=qdrant_url)
        else:
            vector_db_path = getattr(request.app, 'vector_db_path', 'assets/database')
            client = QdrantClient(path=vector_db_path)

        client.delete_collection(collection_name=collection_name)

        return JSONResponse(
            content={"signal": "COLLECTION_DELETED", "collection_name": collection_name}
        )

    except Exception as e:
        logger.error(f"Error deleting collection: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": "ERROR_DELETING_COLLECTION", "error": str(e)}
        )

