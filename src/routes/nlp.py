from fastapi import FastAPI, APIRouter, status, Request, Depends
from fastapi.responses import JSONResponse
from routes.schemes.nlp import PushRequest, SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers import NLPController
from models import ResponseSignal
from helpers.auth import require_admin, get_current_user
from tqdm.auto import tqdm

import logging
import asyncio

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: int, push_request: PushRequest,
                       current_user: dict = Depends(require_admin)):

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
    
    # Initialize NLPController with LangChain services
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

    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    # setup batching
    total_chunks_count = await chunk_model.get_total_chunks_count(project_id=project.project_id)
    pbar = tqdm(total=total_chunks_count, desc="Vector Indexing", position=0)

    while has_records:
        page_chunks = await chunk_model.get_project_chunks(project_id=project.project_id, page_no=page_no)
        if len(page_chunks):
            page_no += 1
        
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunks_ids =  [ c.chunk_id for c in page_chunks ]
        idx += len(page_chunks)
        
        is_inserted = await nlp_controller.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            chunks_ids=chunks_ids
        )

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
                }
            )

        pbar.update(len(page_chunks))
        inserted_items_count += len(page_chunks)
        
    return JSONResponse(
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )

@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: int,
                                current_user: dict = Depends(require_admin)):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    # Initialize NLPController with LangChain services
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

    collection_info = await nlp_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )

@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: int, search_request: SearchRequest,
                      current_user: dict = Depends(get_current_user)):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    # Define a function that does ALL blocking operations in a thread
    def _process_search_sync():
        # Initialize NLPController - THIS is the blocking part!
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

        # Call sync method
        return nlp_controller.search_vector_db_collection(
            project=project,
            text=search_request.text,
            limit=search_request.limit
        )

    # Execute EVERYTHING in a separate thread using asyncio.to_thread
    results = await asyncio.to_thread(_process_search_sync)

    if not results:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.VECTORDB_SEARCH_ERROR.value
                }
            )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            "results": results  # Already dict format from NLPController
        }
    )

@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: int, search_request: SearchRequest,
                    current_user: dict = Depends(get_current_user)):
    """
    Génère une réponse RAG avec support optionnel de l'historique conversationnel

    Si conversation_id est fourni :
    - Récupère l'historique de la conversation
    - Inclut l'historique dans le contexte du LLM
    - Sauvegarde la question et la réponse dans la base de données
    """

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    # NOUVEAU : Gérer l'historique conversationnel
    conversation_history = None
    conversation_model = None
    conversation = None

    if search_request.conversation_id:
        # Importer ConversationModel
        from models.ConversationModel import ConversationModel
        from models.UserModel import UserModel

        conversation_model = ConversationModel(db_client=request.app.db_client)

        # Récupérer la conversation
        conversation = await conversation_model.get_conversation(search_request.conversation_id)

        if not conversation:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"signal": "CONVERSATION_NOT_FOUND"}
            )

        # Vérifier que l'utilisateur est propriétaire de la conversation
        user_model = UserModel(db_client=request.app.db_client)
        user = await user_model.get_user_by_username(current_user["username"])

        if conversation.user_id != user.user_id:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"signal": "CONVERSATION_ACCESS_DENIED"}
            )

        # Récupérer les messages précédents pour construire l'historique
        messages = await conversation_model.get_conversation_messages(search_request.conversation_id)

        # Formatter l'historique pour le LLM
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    # Initialize NLPController
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

    # Use ASYNC method directly (no thread wrapping needed)
    answer, full_prompt, chat_history = await nlp_controller.aanswer_rag_question(
        project=project,
        query=search_request.text,
        limit=search_request.limit,
        conversation_history=conversation_history
    )

    if not answer:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.RAG_ANSWER_ERROR.value
                }
        )

    # NOUVEAU : Sauvegarder la question et la réponse si conversation_id fourni
    if search_request.conversation_id and conversation_model:
        # Sauvegarder la question de l'utilisateur
        await conversation_model.add_message(
            conversation_id=search_request.conversation_id,
            role="user",
            content=search_request.text
        )

        # Sauvegarder la réponse de l'assistant
        await conversation_model.add_message(
            conversation_id=search_request.conversation_id,
            role="assistant",
            content=answer
        )

        # Mettre à jour le titre si c'est la première question
        if conversation and (not conversation.title or conversation.title == "Nouvelle conversation"):
            # Générer un titre depuis la première question (max 60 caractères)
            title = search_request.text[:60] + "..." if len(search_request.text) > 60 else search_request.text
            await conversation_model.update_conversation_title(
                search_request.conversation_id,
                title
            )

    return JSONResponse(
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history,
            "conversation_id": search_request.conversation_id  # Retourner l'ID pour le frontend
        }
    )