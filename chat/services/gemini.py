import logging

from django.conf import settings
from google import genai
from google.genai import types

from chat.tools import ALL_TOOLS, execute_tool
from google.genai.errors import ClientError, ServerError

from chat.prompts.prompt_loader import load_system_prompt

from chat.exceptions import GeminiClientUnavailableError, GeminiRateLimitError, GeminiServerUnavailableError, GeminiServiceError

logger = logging.getLogger(__name__)


client = genai.Client(api_key=settings.GOOGLE_API_KEY)

MODEL = settings.GEMINI_MODEL
TEMPERATURE = settings.GEMINI_TEMPERATURE


SYSTEM_PROMPT = load_system_prompt()


def generate_response(contents, user_id=None):
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=TEMPERATURE,
                tools=ALL_TOOLS,
            ),
        )

        function_call = _get_function_call(response)

        if function_call:
            tool_args = dict(function_call.args or {})

            logger.info(
                "Gemini requested tool: %s with args: %s",
                function_call.name,
                tool_args,
            )

            tool_result = execute_tool(
                function_call.name,
                tool_args,
                user_id=user_id,
            )

            logger.info(
                "Tool result for %s: %s",
                function_call.name,
                tool_result,
            )

            updated_contents = list(contents)

            updated_contents.append(response.candidates[0].content)

            updated_contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_function_response(
                            name=function_call.name,
                            response={
                                "result": tool_result,
                            },
                        )
                    ],
                )
            )

            final_response = client.models.generate_content(
                model=MODEL,
                contents=updated_contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=TEMPERATURE,
                ),
            )

            return final_response.text or "I could not generate a response."

        return response.text or "I could not generate a response."

    except ServerError as e:
        logger.exception("Gemini API server error")

        if "503" in str(e) or "UNAVAILABLE" in str(e):
            raise GeminiServerUnavailableError() from e

        raise GeminiServiceError(
            "Gemini API server error. Please try again later."
        ) from e

    except ClientError as e:
        logger.exception("Gemini API client error")

        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            raise GeminiRateLimitError() from e

        raise GeminiClientUnavailableError() from e

    except Exception as e:
        logger.exception("Gemini response generation failed")

        raise GeminiServiceError() from e


def _get_function_call(response):
    if not response.candidates:
        return None

    candidate = response.candidates[0]

    if not candidate.content or not candidate.content.parts:
        return None

    for part in candidate.content.parts:
        if getattr(part, "function_call", None):
            return part.function_call

    return None