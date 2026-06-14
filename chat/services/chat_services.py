from google.genai import types

from chat.models import Conversation, Message


def get_or_create_conversation(user, conversation_id=None):
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
        title="Airport AI Chat",
    )


def prepare_chat_context(user, user_content: str, conversation_id=None):
    conversation = get_or_create_conversation(user, conversation_id)

    Message.objects.create(
        conversation=conversation,
        role=Message.Role.USER,
        content=user_content,
    )

    messages = list(
        conversation.messages
        .order_by("-created_at")[:15]
    )

    messages.reverse()

    contents = []

    for message in messages:
        role = "model" if message.role == Message.Role.ASSISTANT else "user"

        contents.append(
            types.Content(
                role=role,
                parts=[
                    types.Part(text=message.content)
                ],
            )
        )

    return conversation, contents


def save_chat_response(conversation, response_text: str):
    return Message.objects.create(
        conversation=conversation,
        role=Message.Role.ASSISTANT,
        content=response_text,
    )