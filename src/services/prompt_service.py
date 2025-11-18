"""
Prompt Service
Modern prompt management using LangChain ChatPromptTemplate
Supports multiple languages (EN, FR, AR)
"""

from typing import List, Literal
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.documents import Document


class PromptService:
    """Service for managing RAG prompts with multi-language support"""

    # System prompts by language
    SYSTEM_PROMPTS = {
        "en": """You are an assistant to generate a response for the user.
You will be provided by a set of documents associated with the user's query.
You have to generate a response based on the documents provided.
Ignore the documents that are not relevant to the user's query.
You can apologize to the user if you are not able to generate a response.
You have to generate response in the same language as the user's query.
Be polite and respectful to the user.
Be precise and concise in your response. Avoid unnecessary information.""",

        "fr": """Vous êtes un assistant chargé de générer une réponse pour l'utilisateur.
Un ensemble de documents liés à la requête de l'utilisateur vous sera fourni.
Vous devez générer une réponse en vous basant sur les documents fournis.
Ignorez les documents qui ne sont pas pertinents pour la requête de l'utilisateur.
Vous pouvez vous excuser auprès de l'utilisateur si vous n'êtes pas en mesure de générer une réponse.
Vous devez répondre dans la même langue que celle utilisée par l'utilisateur.
Soyez poli et respectueux envers l'utilisateur.
Soyez précis et concis dans votre réponse. Évitez les informations inutiles.""",

        "ar": """أنت مساعد لتوليد استجابة للمستخدم.
سيتم تزويدك بمجموعة من الوثائق المرتبطة باستفسار المستخدم.
يجب عليك توليد استجابة بناءً على الوثائق المقدمة.
تجاهل الوثائق غير ذات الصلة باستفسار المستخدم.
يمكنك الاعتذار للمستخدم إذا لم تتمكن من توليد استجابة.
يجب أن تولد الاستجابة بنفس لغة استفسار المستخدم.
كن مهذباً ومحترماً مع المستخدم.
كن دقيقاً وموجزاً في ردك. تجنب المعلومات غير الضرورية."""
    }

    # Footer prompts by language
    FOOTER_PROMPTS = {
        "en": """Based only on the above documents, please generate an answer for the user.

## Question:
{question}

## Answer:""",

        "fr": """En vous basant uniquement sur les documents ci-dessus, veuillez générer une réponse pour l'utilisateur.

## Question :
{question}

## Réponse :""",

        "ar": """استناداً فقط إلى الوثائق أعلاه، يرجى توليد إجابة للمستخدم.

## السؤال:
{question}

## الإجابة:"""
    }

    def __init__(self, language: Literal["en", "fr", "ar"] = "en"):
        """
        Initialize PromptService

        Args:
            language: Language for prompts ("en", "fr", "ar")
        """
        self.language = language
        self.system_prompt = self.SYSTEM_PROMPTS.get(language, self.SYSTEM_PROMPTS["en"])
        self.footer_template = self.FOOTER_PROMPTS.get(language, self.FOOTER_PROMPTS["en"])

    def format_documents(self, documents: List[Document], language: str = None) -> str:
        """
        Format documents for RAG context

        Args:
            documents: List of Document objects
            language: Language for formatting (overrides instance language)

        Returns:
            Formatted documents string
        """
        lang = language or self.language

        # Document headers by language
        doc_headers = {
            "en": "## Document No: {num}\n### Content: {content}\n",
            "fr": "## Document n° : {num}\n### Contenu : {content}\n",
            "ar": "## الوثيقة رقم: {num}\n### المحتوى: {content}\n"
        }

        header_template = doc_headers.get(lang, doc_headers["en"])

        formatted_docs = []
        for i, doc in enumerate(documents, 1):
            formatted_doc = header_template.format(
                num=i,
                content=doc.page_content
            )
            formatted_docs.append(formatted_doc)

        return "\n".join(formatted_docs)

    def create_rag_prompt(self) -> ChatPromptTemplate:
        """
        Create RAG ChatPromptTemplate for LangChain

        Returns:
            ChatPromptTemplate for RAG
        """
        template = f"""{self.system_prompt}

{{context}}

{self.footer_template}"""

        return ChatPromptTemplate.from_template(template)

    def create_conversational_rag_prompt(self) -> ChatPromptTemplate:
        """
        Create conversational RAG prompt with chat history

        Returns:
            ChatPromptTemplate for conversational RAG
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("system", "Here are the relevant documents:\n\n{context}"),
            ("placeholder", "{chat_history}"),
            ("human", "{question}")
        ])

        return prompt

    def get_simple_prompt(self, question: str, context: str) -> str:
        """
        Get simple formatted prompt string (for direct LLM calls)

        Args:
            question: User question
            context: Context documents

        Returns:
            Formatted prompt string
        """
        return f"""{self.system_prompt}

{context}

{self.footer_template.format(question=question)}"""

    def set_language(self, language: Literal["en", "fr", "ar"]):
        """
        Change the prompt language

        Args:
            language: New language
        """
        if language not in self.SYSTEM_PROMPTS:
            raise ValueError(f"Unsupported language: {language}")

        self.language = language
        self.system_prompt = self.SYSTEM_PROMPTS[language]
        self.footer_template = self.FOOTER_PROMPTS[language]

    def get_language_info(self) -> dict:
        """Get current language information"""
        return {
            "current_language": self.language,
            "supported_languages": list(self.SYSTEM_PROMPTS.keys())
        }


# Convenience functions for quick access
def get_rag_prompt(language: str = "en") -> ChatPromptTemplate:
    """
    Quick access to RAG prompt

    Args:
        language: Prompt language

    Returns:
        ChatPromptTemplate
    """
    service = PromptService(language=language)
    return service.create_rag_prompt()


def get_conversational_rag_prompt(language: str = "en") -> ChatPromptTemplate:
    """
    Quick access to conversational RAG prompt

    Args:
        language: Prompt language

    Returns:
        ChatPromptTemplate
    """
    service = PromptService(language=language)
    return service.create_conversational_rag_prompt()
