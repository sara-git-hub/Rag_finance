from models.BaseDataModel import BaseDataModel
from models.db_schemes.minirag.schemes.conversation import Conversation, Message, ConversationStatus
from sqlalchemy import select, and_, desc
import json

class ConversationModel(BaseDataModel):
    """
    Modèle pour gérer les conversations et messages.
    Suit le pattern des autres modèles (UserModel, ProjectModel, etc.)
    """

    async def create_conversation(self, user_id: int, project_id: int, title: str = None):
        """
        Créer une nouvelle conversation

        Args:
            user_id: ID de l'utilisateur qui démarre la conversation
            project_id: ID du projet concerné
            title: Titre optionnel (sera généré automatiquement si None)

        Returns:
            Conversation: La conversation créée
        """
        async with self.db_client() as session:
            conversation = Conversation(
                user_id=user_id,
                project_id=project_id,
                title=title or "Nouvelle conversation",
                status=ConversationStatus.ACTIVE
            )
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            return conversation

    async def get_conversation(self, conversation_id: int):
        """
        Récupérer une conversation par son ID

        Args:
            conversation_id: ID de la conversation

        Returns:
            Conversation ou None
        """
        async with self.db_client() as session:
            result = await session.execute(
                select(Conversation).where(Conversation.conversation_id == conversation_id)
            )
            return result.scalar_one_or_none()

    async def get_user_conversations(self, user_id: int, project_id: int = None,
                                     status: ConversationStatus = None):
        """
        Récupérer toutes les conversations d'un utilisateur

        Args:
            user_id: ID de l'utilisateur
            project_id: Optionnel - filtrer par projet
            status: Optionnel - filtrer par statut (ACTIVE, ARCHIVED)

        Returns:
            Liste de Conversations, triées par date de modification décroissante
        """
        async with self.db_client() as session:
            query = select(Conversation).where(Conversation.user_id == user_id)

            # Filtres optionnels
            if project_id:
                query = query.where(Conversation.project_id == project_id)
            if status:
                query = query.where(Conversation.status == status)

            # Trier par date de modification (plus récent en premier)
            query = query.order_by(desc(Conversation.updated_at))

            result = await session.execute(query)
            return result.scalars().all()

    async def update_conversation_title(self, conversation_id: int, title: str):
        """
        Mettre à jour le titre d'une conversation

        Args:
            conversation_id: ID de la conversation
            title: Nouveau titre

        Returns:
            Conversation mise à jour ou None
        """
        async with self.db_client() as session:
            result = await session.execute(
                select(Conversation).where(Conversation.conversation_id == conversation_id)
            )
            conversation = result.scalar_one_or_none()

            if conversation:
                conversation.title = title
                await session.commit()
                await session.refresh(conversation)

            return conversation

    async def archive_conversation(self, conversation_id: int):
        """
        Archiver une conversation (change le statut à ARCHIVED)

        Args:
            conversation_id: ID de la conversation

        Returns:
            Conversation archivée ou None
        """
        async with self.db_client() as session:
            result = await session.execute(
                select(Conversation).where(Conversation.conversation_id == conversation_id)
            )
            conversation = result.scalar_one_or_none()

            if conversation:
                conversation.status = ConversationStatus.ARCHIVED
                await session.commit()
                await session.refresh(conversation)

            return conversation

    async def add_message(self, conversation_id: int, role: str, content: str, metadata: dict = None):
        """
        Ajouter un message à une conversation

        Args:
            conversation_id: ID de la conversation
            role: "user" ou "assistant"
            content: Contenu du message
            metadata: Métadonnées optionnelles (sources RAG, scores, etc.)

        Returns:
            Message créé
        """
        async with self.db_client() as session:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                metadata=json.dumps(metadata) if metadata else None
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message

    async def get_conversation_messages(self, conversation_id: int, limit: int = 100):
        """
        Récupérer tous les messages d'une conversation

        Args:
            conversation_id: ID de la conversation
            limit: Nombre maximum de messages à retourner (défaut 100)

        Returns:
            Liste de Messages, triés par date de création croissante (plus ancien en premier)
        """
        async with self.db_client() as session:
            result = await session.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.asc())
                .limit(limit)
            )
            return result.scalars().all()

    async def get_last_n_messages(self, conversation_id: int, n: int = 10):
        """
        Récupérer les N derniers messages d'une conversation
        Utile pour construire l'historique du contexte LLM

        Args:
            conversation_id: ID de la conversation
            n: Nombre de messages à récupérer

        Returns:
            Liste des N derniers Messages, triés chronologiquement
        """
        async with self.db_client() as session:
            # Récupérer les N derniers messages
            result = await session.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(desc(Message.created_at))
                .limit(n)
            )
            messages = result.scalars().all()

            # Inverser pour avoir l'ordre chronologique
            return list(reversed(messages))

    async def delete_conversation(self, conversation_id: int):
        """
        Supprimer complètement une conversation et tous ses messages
        (Attention : opération irréversible !)

        Args:
            conversation_id: ID de la conversation

        Returns:
            True si supprimé, False sinon
        """
        async with self.db_client() as session:
            # D'abord supprimer tous les messages
            await session.execute(
                select(Message).where(Message.conversation_id == conversation_id)
            )

            # Ensuite supprimer la conversation
            result = await session.execute(
                select(Conversation).where(Conversation.conversation_id == conversation_id)
            )
            conversation = result.scalar_one_or_none()

            if conversation:
                await session.delete(conversation)
                await session.commit()
                return True

            return False
