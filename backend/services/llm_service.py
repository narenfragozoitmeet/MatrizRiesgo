"""Servicio LLM usando emergentintegrations"""

import os
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from core.config import settings
import logging
import asyncio

load_dotenv()

logger = logging.getLogger(__name__)

class LLMService:
    """Servicio centralizado para interactuar con LLMs via emergentintegrations"""
    
    def __init__(self):
        self.api_key = settings.EMERGENT_LLM_KEY
        self.provider = settings.LLM_MODEL_PROVIDER
        self.model = settings.LLM_MODEL_NAME
        logger.info(f"🤖 LLM Service inicializado: {self.provider}/{self.model}")
    
    async def generate(
        self,
        prompt: str,
        system_message: str = "Eres un experto asistente en análisis de riesgos.",
        session_id: str = "default"
    ) -> str:
        """
        Genera respuesta del LLM
        
        Args:
            prompt: Prompt del usuario
            system_message: Mensaje del sistema (contexto)
            session_id: ID de sesión único
            
        Returns:
            Respuesta del LLM en texto
        """
        try:
            # Inicializar chat
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=system_message
            ).with_model(self.provider, self.model)
            
            # Crear mensaje de usuario
            user_message = UserMessage(text=prompt)
            
            # Enviar y obtener respuesta
            response = await chat.send_message(user_message)
            
            logger.info(f"✅ LLM respuesta recibida ({len(response)} chars)")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error en LLM: {str(e)}")
            raise Exception(f"Error generando respuesta: {str(e)}")
    
    def generate_sync(
        self,
        prompt: str,
        system_message: str = "Eres un experto asistente en análisis de riesgos.",
        session_id: str = "default"
    ) -> str:
        """Versión síncrona de generate()"""
        return asyncio.run(self.generate(prompt, system_message, session_id))

# Instancia singleton
llm_service = LLMService()
