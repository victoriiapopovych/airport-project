import json
import logging
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from user.models import User
from .services.chat_services import prepare_chat_context, save_chat_response

from .services.gemini import generate_response

from .exceptions import GeminiServiceError

logger = logging.getLogger(__name__)

prepare_chat_context_async = database_sync_to_async(prepare_chat_context)
save_chat_response_async = database_sync_to_async(save_chat_response)


@database_sync_to_async
def get_user_from_token(token: str):
    if not token:
        return None

    try:
        validated_token = AccessToken(token)
        user_id = validated_token["user_id"]

        return User.objects.get(id=user_id)

    except (TokenError, InvalidToken):
        logger.warning("Invalid or expired WebSocket token")
        return None

    except User.DoesNotExist:
        logger.warning("WebSocket user not found")
        return None


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope["query_string"].decode()
        params = parse_qs(query_string)

        token = params.get("token", [None])[0]
        user = await get_user_from_token(token)

        if not user:
            await self.close(code=4001)
            return

        self.user = user
        await self.accept()

        await self.send(text_data=json.dumps({
            "type": "system",
            "message": "Connected to Airport AI Chat."
        }))

    async def disconnect(self, close_code):
        logger.info(
            "WebSocket disconnected. User=%s, code=%s",
            getattr(self, "user", None),
            close_code,
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Invalid JSON format."
            }))
            return

        content = data.get("content", "").strip()
        conversation_id = data.get("conversation_id")

        if not content:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Content is required."
            }))
            return

        conversation, contents = await prepare_chat_context_async(
            self.user,
            content,
            conversation_id,
        )

        try:
            response_text = await database_sync_to_async(generate_response)(
                contents,
                self.user.id,
            )
        except GeminiServiceError as e:
            response_text = e.message

        await save_chat_response_async(
            conversation,
            response_text,
        )

        await self.send(text_data=json.dumps({
            "type": "assistant",
            "conversation_id": conversation.id,
            "message": response_text,
        }))