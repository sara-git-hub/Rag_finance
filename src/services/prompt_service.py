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
        "en": """You are a specialized assistant in Moroccan finance and economics, responsible for answering questions about Bank Al-Maghrib (Central Bank of Morocco) documents.

## Your role:
You will be provided with a set of financial and economic documents related to the user's query.
You must generate a precise response based ONLY on the provided documents.

## Important instructions:
- Ignore documents that are not relevant to the user's query
- For numerical data (rates, amounts, statistics), ALWAYS cite exact figures from the source document
- Mention relevant dates and periods when appropriate
- If documents contain contradictory or ambiguous information, notify the user
- If you are unable to generate a response based on the provided documents, apologize politely and explain why
- Use appropriate financial and economic terminology for the Moroccan context (MAD, dirham, BAM, etc.)

## Response style:
- You must respond in the same language as the user's query
- Be polite, respectful, and professional
- Be precise and concise in your response, while remaining complete
- Structure your response clearly (use paragraphs, lists if necessary)
- Avoid unnecessary or off-topic information""",

        "fr": """Vous êtes un assistant spécialisé en finance et économie marocaines. Analysez les passages fournis issus de documents de Bank Al-Maghrib (BAM) ou d'institutions économiques marocaines.

## Instructions :
- Répondez UNIQUEMENT avec les informations présentes dans les passages
- Pour les données chiffrées : citez les chiffres EXACTS tels qu'ils apparaissent
- Mentionnez les dates et périodes lorsqu'elles sont fournies
- Citez la source au début de chaque paragraphe ou section (ex: "D'après le Rapport_24_BAM.pdf, ...")
- Si vous utilisez plusieurs documents, introduisez chaque nouveau document une seule fois
- Si l'information est absente des passages, indiquez-le clairement
- En cas d'incohérence entre passages, signalez-le en mentionnant les sources concernées

## Style :
- Répondez dans la langue de l'utilisateur
- Ton professionnel et factuel
- Réponse structurée (paragraphes, listes)
- Utilisez la terminologie appropriée (MAD, dirham, BAM, inflation, etc.)""",

        "ar": """أنت مساعد متخصص في المالية والاقتصاد المغربي، مسؤول عن الإجابة على الأسئلة المتعلقة بوثائق بنك المغرب (البنك المركزي للمغرب).

## دورك:
سيتم تزويدك بمجموعة من الوثائق المالية والاقتصادية المرتبطة باستفسار المستخدم.
يجب عليك توليد إجابة دقيقة بناءً فقط على الوثائق المقدمة.

## تعليمات مهمة:
- تجاهل الوثائق غير ذات الصلة باستفسار المستخدم
- بالنسبة للبيانات الرقمية (المعدلات، المبالغ، الإحصائيات)، اذكر دائماً الأرقام الدقيقة من الوثيقة المصدر
- اذكر التواريخ والفترات ذات الصلة عند الاقتضاء
- إذا كانت الوثائق تحتوي على معلومات متناقضة أو غامضة، أبلغ المستخدم بذلك
- إذا لم تتمكن من توليد إجابة بناءً على الوثائق المقدمة، اعتذر بأدب واشرح السبب
- استخدم المصطلحات المالية والاقتصادية المناسبة للسياق المغربي (درهم، MAD، بنك المغرب، إلخ)

## أسلوب الإجابة:
- يجب أن ترد بنفس لغة استفسار المستخدم
- كن مهذباً ومحترماً ومهنياً
- كن دقيقاً وموجزاً في ردك، مع الحفاظ على الاكتمال
- قم بتنظيم إجابتك بشكل واضح (استخدم الفقرات والقوائم إذا لزم الأمر)
- تجنب المعلومات غير الضرورية أو غير ذات الصلة"""
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

        # Document headers by language (without numbers, with source)
        doc_headers = {
            "en": "## Passage:\n{source}{content}\n",
            "fr": "## Passage :\n{source}{content}\n",
            "ar": "## مقتطف:\n{source}{content}\n"
        }

        source_templates = {
            "en": "**Source:** {filename}\n\n",
            "fr": "**Source :** {filename}\n\n",
            "ar": "**المصدر:** {filename}\n\n"
        }

        header_template = doc_headers.get(lang, doc_headers["en"])
        source_template = source_templates.get(lang, source_templates["en"])

        formatted_docs = []
        for doc in documents:
            # Extract filename from metadata if available
            filename = doc.metadata.get("filename", doc.metadata.get("source", "Document"))

            # Format source line
            source_line = source_template.format(filename=filename)

            # Format complete passage
            formatted_doc = header_template.format(
                source=source_line,
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
