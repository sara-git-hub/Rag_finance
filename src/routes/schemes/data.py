from pydantic import BaseModel, field_validator
from typing import Optional, Literal

class ProcessRequest(BaseModel):
    file_id : str = None
    chunk_size : Optional[int] = 100
    overlap_size : Optional[int] = 20
    do_reset : Optional[int] = 0

class ProjectLanguageRequest(BaseModel):
    """Request to update project language"""
    language: Literal["fr", "en", "ar"]

    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        if v not in ["fr", "en", "ar"]:
            raise ValueError('Language must be one of: fr, en, ar')
        return v