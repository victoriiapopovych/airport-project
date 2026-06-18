from django.conf import settings
from django.core.cache import cache
from google.genai import types

from chat.models import Conversation, Message


def get_chat_cache_key(conversation_id):
    return f"chat_context:{conversation_id}"


def get_or_create_conversation(user, conversation_id=None, title=None):
    if conversation_id:
        conversation = Conversation.objects.filter(
            id=conversation_id,
            user=user,
            is_active=True,
        ).first()

        if conversation:
            return conversation

    return Conversation.objects.create(
        user=user,
        title=title or "New chat",
    )


def message_to_gemini_content(message_data):
    role = "model" if message_data["role"] == Message.Role.ASSISTANT else "user"

    return types.Content(
        role=role,
        parts=[types.Part(text=message_data["content"])],
    )


def load_context_from_db(conversation):
    messages = list(
        conversation.messages.order_by("-created_at")[
            :settings.CHAT_CONTEXT_MESSAGES_LIMIT
        ]
    )

    messages.reverse()

    context = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]

    cache.set(
        get_chat_cache_key(conversation.id),
        context,
        timeout=settings.CHAT_CONTEXT_CACHE_TIMEOUT,
    )

    return context


def append_message_to_cache(conversation_id, role, content):
    cache_key = get_chat_cache_key(conversation_id)

    context = cache.get(cache_key)

    if context is None:
        context = []

    context.append({
        "role": role,
        "content": content,
    })

    context = context[-settings.CHAT_CONTEXT_MESSAGES_LIMIT:]

    cache.set(
        cache_key,
        context,
        timeout=settings.CHAT_CONTEXT_CACHE_TIMEOUT,
    )

    return context


def prepare_chat_context(user, user_content: str, conversation_id=None):
    conversation = get_or_create_conversation(
        user,
        conversation_id,
        title=user_content[:60],
    )

    Message.objects.create(
        conversation=conversation,
        role=Message.Role.USER,
        content=user_content,
    )

    cache_key = get_chat_cache_key(conversation.id)
    context = cache.get(cache_key)

    if context is None:
        context = load_context_from_db(conversation)
    else:
        context = append_message_to_cache(
            conversation.id,
            Message.Role.USER,
            user_content,
        )

    contents = [
        message_to_gemini_content(message_data)
        for message_data in context
    ]

    return conversation, contents


def save_chat_response(conversation, response_text: str):
    message = Message.objects.create(
        conversation=conversation,
        role=Message.Role.ASSISTANT,
        content=response_text,
    )

    append_message_to_cache(
        conversation.id,
        Message.Role.ASSISTANT,
        response_text,
    )

    return message 