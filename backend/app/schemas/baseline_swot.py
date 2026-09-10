from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class BaselineFinding(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    source_type: Literal['BUSINESS_BASELINE'] = 'BUSINESS_BASELINE'
    importance: Literal['LOW', 'MEDIUM'] = 'LOW'


class BaselineSwot(BaseModel):
    model_config = ConfigDict(extra='forbid')
    version: str = Field(min_length=1)
    strengths: list[BaselineFinding]
    weaknesses: list[BaselineFinding]
    opportunities: list[BaselineFinding]
    threats: list[BaselineFinding]
