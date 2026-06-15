import logging

from django.conf import settings
from google import genai
from google.genai import types

from chat.tools import ALL_TOOLS, execute_tool
from google.genai.errors import ClientError, ServerError

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
- Never show bookings, tickets, or lounge accesses belonging to another user.
- ALWAYS use tools when the user asks about real system data.
- Never generate or guess system data from your own knowledge.
- Do not invent flights, seats, bookings, tickets, lounge accesses, prices, airports, airlines, or times.
- If a tool returns an empty list, clearly say that no matching records were found.
- If a suitable tool exists for the request, use the tool instead of asking follow-up questions.

Flight search rules:
- For any flight search request, call get_available_flights.
- All flight search filters are optional.
- If the user gives only an airline, search by airline.
- If the user gives only a date, search by date.
- If the user gives only a departure city or airport, search by that.
- If the user gives only an arrival city or airport, search by that.
- Do not ask for missing filters if a general search can be performed.

Airport rules:
- For airport list or airport search requests, call get_airports.
- For requests to show all airports, call get_airports without filters.
- For questions about a specific airport, call get_airport_details.

Airline rules:
- For airline list or airline search requests, call get_airlines.
- For requests to show all airlines, call get_airlines without filters.
- For questions about a specific airline, call get_airline_details.

Seat rules:
- For seat availability questions, call get_available_seats.
- For questions about a specific seat, call get_seat_details.

Booking rules:
- For any request asking to show, list, display, find, or retrieve the user's bookings, ALWAYS call get_user_bookings.
- If the user does not provide a filter, show all bookings.
- Do not ask which bookings the user wants unless they explicitly request filtering.
- For requests about a specific booking, call get_booking_details.

Ticket rules:
- For any request asking to show, list, display, find, or retrieve the user's tickets, ALWAYS call get_user_tickets.
- If the user does not provide a filter, show all tickets.
- Do not ask which tickets the user wants unless they explicitly request filtering.
- For requests about a specific ticket, call get_ticket_details.

Lounge rules:
- For lounge search requests, call get_available_lounges.
- For requests about a specific lounge, call get_lounge_details.
- For any request asking to show the user's lounge accesses, ALWAYS call get_user_lounge_accesses.
- If the user does not provide a filter, show all lounge accesses.
- Do not ask follow-up questions when all lounge accesses can be shown directly.
- For requests about a specific lounge access, call get_lounge_access_details.

Response style:
- Be friendly and conversational.
- Prefer showing tool results over explaining them.
- Present information in a structured format.
- When displaying lists, clearly separate records with empty lines.
- When displaying detailed information, show all important fields returned by the tool.
- Do not summarize tool results if important information would be lost.
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
            return (
                "Gemini API is currently overloaded. "
                "Please try again later."
            )

        return (
            "Gemini API server error. "
            "Please try again later."
        )

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