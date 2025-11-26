from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

class ConversationStatus(str, enum.Enum):
    """Statut d'une conversation"""
    ACTIVE = "active"
    ARCHIVED = "archived"

class Conversation(SQLAlchemyBase):
    """
    Table des conversations : Une conversation = une session de chat avec un projet
    Regroupe plusieurs messages (questions/réponses)
    """
    __tablename__ = "conversations"

    # Identifiants
    conversation_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    conversation_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    # Relations avec autres tables
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False, index=True)

    # Métadonnées de la conversation
    title = Column(String(200), nullable=True)  # Généré automatiquement depuis 1ère question
    status = Column(
        Enum(ConversationStatus, values_callable=lambda x: [e.value for e in x]),
        default=ConversationStatus.ACTIVE,
        nullable=False
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


class Message(SQLAlchemyBase):
    """
    Table des messages : Un message = une question utilisateur OU une réponse assistant
    Appartient à une conversation
    """
    __tablename__ = "messages"

    # Identifiant
    message_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Relation avec conversation
    conversation_id = Column(Integer, ForeignKey("conversations.conversation_id"), nullable=False, index=True)

    # Contenu du message
    role = Column(String(20), nullable=False)  # "user" ou "assistant"
    content = Column(Text, nullable=False)  # Le texte du message
    message_metadata = Column(Text, nullable=True)  # JSON: sources RAG, scores, tokens utilisés, etc.

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
