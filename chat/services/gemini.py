import logging

from django.conf import settings
from google import genai
from google.genai import types

from chat.tools import ALL_TOOLS, execute_tool
from google.genai.errors import ClientError

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GOOGLE_API_KEY)

MODEL = "gemini-2.5-flash-lite"
TEMPERATURE = 0.3


SYSTEM_PROMPT = """
You are Airport AI, a helpful assistant inside an Airport Management System.

You can help users with:
- real airport data stored in the system
- flights
- routes
- airports
- airlines
- seats
- bookings
- tickets
- lounge access
- explanations of how this Airport Management System works

If the user asks about topics unrelated to the airport system, politely refuse and say:
"I can help only with questions related to the airport system."

You may answer without tools when the user asks general questions about how the system works, for example:
- How does booking work?
- What is lounge access?
- What flight statuses exist?
- How can I choose a seat?

Data rules:
- Use tools whenever the user asks about real system data.
- Do not invent flights, seats, bookings, tickets, prices, airports, or times.
- If a tool returns an empty list, clearly say that no matching records were found.

Flight search rules:
- For any flight search request, call get_available_flights.
- All flight search filters are optional.
- If the user gives only an airline, search by airline.
- If the user gives only a date, search by date.
- If the user gives only a departure city or airport, search by that.
- If the user gives only an arrival city or airport, search by that.
- Do not ask for missing filters if a general search can be performed.

Seat rules:
- For seat availability questions, call get_available_seats.
- For questions about a specific seat, call get_seat_details.

Response style:
- Be friendly, clear, and natural.
- Do not sound robotic.
- Use short paragraphs.
- Format information neatly with line breaks.
- Do not use markdown syntax.
- Do not use *, **, #, or bullet markdown.
- Prefer this style:

Here are the available flights I found:

LH123 — Lufthansa
From: Berlin Brandenburg Airport
To: Munich Airport
Departure: 2026-07-01 10:00
Arrival: 2026-07-01 11:10
Terminal: A
Gate: B12

If useful, tell the user what they can ask next, for example:
"You can also ask me about available seats or flight details."

Answer in the same language as the user.
"""


def generate_response(contents):
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
            tool_result = execute_tool(
                function_call.name,
                dict(function_call.args or {}),
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

    except ClientError as e:
        logger.exception("Gemini API client error")

        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return (
                "Gemini API rate limit exceeded. "
                "Please try again later."
            )

        return (
            "Gemini API is temporarily unavailable. "
            "Please try again later."
        )

    except Exception:
        logger.exception("Gemini response generation failed")

        return (
            "Internal AI assistant error. "
            "Please try again later."
        )

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