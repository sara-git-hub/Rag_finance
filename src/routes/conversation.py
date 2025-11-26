from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from helpers.auth import get_current_user
from models.ConversationModel import ConversationModel
from models.db_schemes.minirag.schemes.conversation import ConversationStatus
from models.db_schemes import Message
from sqlalchemy.future import select
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
import logging

logger = logging.getLogger('uvicorn.error')

conversation_router = APIRouter(
    prefix="/api/v1/conversations",
    tags=["conversations"],
)

# ============= Schemas Pydantic =============

class CreateConversationRequest(BaseModel):
    """Schema pour créer une conversation"""
    project_id: int
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    """Schema de réponse pour une conversation"""
    conversation_id: int
    project_id: int
    title: str
    status: str
    created_at: str
    updated_at: Optional[str] = None

class MessageResponse(BaseModel):
    """Schema de réponse pour un message"""
    message_id: int
    role: str
    content: str
    created_at: str

# ============= Routes =============

@conversation_router.post("/create")
async def create_conversation(
    request: Request,
    body: CreateConversationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Créer une nouvelle conversation pour un projet

    - **project_id**: ID du projet
    - **title**: Titre optionnel (généré automatiquement si non fourni)

    Retourne la conversation créée avec son ID unique
    """
    try:
        conversation_model = ConversationModel(db_client=request.app.db_client)

        # Récupérer l'ID utilisateur depuis le token JWT
        # Note: Assurez-vous que get_current_user retourne "username"
        from models.UserModel import UserModel
        user_model = UserModel(db_client=request.app.db_client)
        user = await user_model.get_user_by_username(current_user["username"])

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        conversation = await conversation_model.create_conversation(
            user_id=user.user_id,
            project_id=body.project_id,
            title=body.title
        )

        return JSONResponse(
            content={
                "conversation_id": conversation.conversation_id,
                "project_id": conversation.project_id,
                "title": conversation.title,
                "status": conversation.status.value,
                "created_at": str(conversation.created_at),
                "updated_at": str(conversation.updated_at) if conversation.updated_at else None
            }
        )

    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@conversation_router.get("/{conversation_id}/messages")
async def get_conversation_messages(
    request: Request,
    conversation_id: int,
    limit: Optional[int] = 100,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer tous les messages d'une conversation

    - **conversation_id**: ID de la conversation
    - **limit**: Nombre maximum de messages (défaut: 100)

    Vérifie que l'utilisateur est propriétaire de la conversation
    """
    try:
        conversation_model = ConversationModel(db_client=request.app.db_client)

        # Vérifier que la conversation existe et appartient à l'utilisateur
        conversation = await conversation_model.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Récupérer l'ID utilisateur
        from models.UserModel import UserModel
        user_model = UserModel(db_client=request.app.db_client)
        user = await user_model.get_user_by_username(current_user["username"])

        if conversation.user_id != user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you don't own this conversation"
            )

        # Récupérer les messages
        messages = await conversation_model.get_conversation_messages(
            conversation_id=conversation_id,
            limit=limit
        )

        return JSONResponse(
            content={
                "conversation_id": conversation_id,
                "messages": [
                    {
                        "message_id": msg.message_id,
                        "role": msg.role,
                        "content": msg.content,
                        "created_at": str(msg.created_at)
                    }
                    for msg in messages
                ]
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@conversation_router.get("/project/{project_id}")
async def list_project_conversations(
    request: Request,
    project_id: int,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Lister toutes les conversations d'un projet pour l'utilisateur actuel

    - **project_id**: ID du projet
    - **status_filter**: Optionnel - filtrer par statut ("active" ou "archived")

    Retourne uniquement les conversations de l'utilisateur connecté
    """
    try:
        conversation_model = ConversationModel(db_client=request.app.db_client)

        # Récupérer l'ID utilisateur
        from models.UserModel import UserModel
        user_model = UserModel(db_client=request.app.db_client)
        user = await user_model.get_user_by_username(current_user["username"])

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Parser le status si fourni
        status_enum = None
        if status_filter:
            try:
                status_enum = ConversationStatus(status_filter)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status_filter}. Must be 'active' or 'archived'"
                )

        # Récupérer les conversations
        conversations = await conversation_model.get_user_conversations(
            user_id=user.user_id,
            project_id=project_id,
            status=status_enum
        )

        # Get message counts for all conversations
        async with request.app.db_client() as session:
            conversation_ids = [conv.conversation_id for conv in conversations]
            if conversation_ids:
                message_count_query = select(
                    Message.conversation_id,
                    func.count(Message.message_id).label('count')
                ).where(
                    Message.conversation_id.in_(conversation_ids)
                ).group_by(Message.conversation_id)

                message_count_result = await session.execute(message_count_query)
                message_counts = {row[0]: row[1] for row in message_count_result}
            else:
                message_counts = {}

        return JSONResponse(
            content={
                "project_id": project_id,
                "conversations": [
                    {
                        "conversation_id": conv.conversation_id,
                        "title": conv.title,
                        "status": conv.status.value,
                        "created_at": str(conv.created_at),
                        "updated_at": str(conv.updated_at) if conv.updated_at else None,
                        "message_count": message_counts.get(conv.conversation_id, 0)
                    }
                    for conv in conversations
                ]
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@conversation_router.delete("/{conversation_id}")
async def delete_conversation(
    request: Request,
    conversation_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Supprimer une conversation et tous ses messages

    - **conversation_id**: ID de la conversation

    ⚠️ Attention: Cette opération est irréversible !
    """
    try:
        conversation_model = ConversationModel(db_client=request.app.db_client)

        # Vérifier que la conversation existe et appartient à l'utilisateur
        conversation = await conversation_model.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Récupérer l'ID utilisateur
        from models.UserModel import UserModel
        user_model = UserModel(db_client=request.app.db_client)
        user = await user_model.get_user_by_username(current_user["username"])

        if conversation.user_id != user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you don't own this conversation"
            )

        # Supprimer la conversation
        deleted = await conversation_model.delete_conversation(conversation_id)

        if deleted:
            return JSONResponse(
                content={
                    "message": "Conversation deleted successfully",
                    "conversation_id": conversation_id
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete conversation"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
