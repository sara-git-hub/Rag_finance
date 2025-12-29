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
        "en": """You are a specialized assistant in Moroccan finance and economics. Analyze the provided passages from Bank Al-Maghrib (BAM) or Moroccan economic institutions documents.

## Instructions:
- Answer ONLY with information present in the passages
- For numerical data: cite EXACT figures as they appear
- Mention dates and periods when provided
- Cite the source at the beginning of each paragraph or section (e.g., "According to Rapport_24_BAM.pdf, ...")
- If using multiple documents, introduce each new document only once
- If information is missing from the passages, clearly indicate it
- In case of inconsistency between passages, report it by mentioning the sources concerned

## MANDATORY response format:
- **CONCISENESS**: Maximum 300 words. Get to the point.
- **STRUCTURE**: Organize your response with numbered key points or short sections
- **COMPLETENESS**: Always end with a complete sentence, never cut off mid-thought
- If the answer requires more details, summarize only the main points

## Style:
- Respond in the user's language
- Professional and factual tone
- Structured response (paragraphs, lists)
- Use appropriate terminology (MAD, dirham, BAM, inflation, etc.)""",

        "fr": """Vous êtes un assistant spécialisé en finance et économie marocaines. Analysez les passages fournis issus de documents de Bank Al-Maghrib (BAM) ou d'institutions économiques marocaines.

## Instructions :
- Répondez UNIQUEMENT avec les informations présentes dans les passages
- Pour les données chiffrées : citez les chiffres EXACTS tels qu'ils apparaissent
- Mentionnez les dates et périodes lorsqu'elles sont fournies
- Citez la source au début de chaque paragraphe ou section (ex: "D'après le Rapport_24_BAM.pdf, ...")
- Si vous utilisez plusieurs documents, introduisez chaque nouveau document une seule fois
- Si l'information est absente des passages, indiquez-le clairement
- En cas d'incohérence entre passages, signalez-le en mentionnant les sources concernées

## Format de réponse OBLIGATOIRE :
- **CONCISION** : Maximum 300 mots. Allez à l'essentiel.
- **STRUCTURE** : Organisez votre réponse avec des points clés numérotés ou des sections courtes
- **COMPLÉTUDE** : Terminez toujours par une phrase complète, ne coupez jamais au milieu d'une idée
- Si la réponse nécessite plus de détails, faites un résumé des points principaux uniquement

## Style :
- Répondez dans la langue de l'utilisateur
- Ton professionnel et factuel
- Réponse structurée (paragraphes, listes)
- Utilisez la terminologie appropriée (MAD, dirham, BAM, inflation, etc.)""",

        "ar": """أنت مساعد متخصص في المالية والاقتصاد المغربي. قم بتحليل المقتطفات المقدمة من وثائق بنك المغرب أو مؤسسات اقتصادية مغربية.

## التعليمات:
- أجب فقط بالمعلومات الموجودة في المقتطفات
- للبيانات الرقمية: اذكر الأرقام الدقيقة كما تظهر
- اذكر التواريخ والفترات عند توفرها
- اذكر المصدر في بداية كل فقرة أو قسم (مثال: "حسب Rapport_24_BAM.pdf، ...")
- إذا كنت تستخدم وثائق متعددة، قدم كل وثيقة جديدة مرة واحدة فقط
- إذا كانت المعلومات غير موجودة في المقتطفات، وضح ذلك بوضوح
- في حالة وجود تناقض بين المقتطفات، أبلغ عنه بذكر المصادر المعنية

## تنسيق الإجابة الإلزامي:
- **الإيجاز**: 300 كلمة كحد أقصى. اذهب مباشرة إلى الموضوع.
- **الهيكلة**: نظم إجابتك بنقاط رئيسية مرقمة أو أقسام قصيرة
- **الاكتمال**: أنهِ دائماً بجملة كاملة، لا تقطع في منتصف فكرة
- إذا كانت الإجابة تتطلب المزيد من التفاصيل، لخص النقاط الرئيسية فقط

## الأسلوب:
- أجب بلغة المستخدم
- نبرة مهنية وواقعية
- إجابة منظمة (فقرات، قوائم)
- استخدم المصطلحات المناسبة (درهم، MAD، بنك المغرب، التضخم، إلخ)"""
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
