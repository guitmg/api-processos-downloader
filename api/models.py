"""
Pydantic models for API request/response validation.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ProcessoRequest(BaseModel):
    """Request model for processo download."""

    numero_processo: str = Field(
        ...,
        description="Número do processo para download",
        example="5100342-29.2017.8.13.0024",
    )


class ProcessoResponse(BaseModel):
    """Response model for processo download initiation."""

    status: str = Field(default="iniciado", description="Status da operação")
    numero_processo: str = Field(..., description="Número do processo que foi iniciado")
    message: Optional[str] = Field(None, description="Mensagem adicional")


class WebhookPayload(BaseModel):
    """Payload model for webhook notification."""

    numero_processo: str = Field(..., description="Número do processo processado")
    status: str = Field(..., description="Status do processamento (sucesso/erro)")
    arquivo_url: Optional[str] = Field(None, description="URL do arquivo baixado")
    arquivo_caminho: Optional[str] = Field(None, description="Caminho local do arquivo")
    erro: Optional[str] = Field(None, description="Descrição do erro, se houver")
