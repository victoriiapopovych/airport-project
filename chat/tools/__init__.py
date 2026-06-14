from google.genai import types

from .flight_tools import get_available_flights, get_flight_details
from .seat_tools import get_available_seats, get_seat_details


available_flights_tool = types.FunctionDeclaration(
    name="get_available_flights",
    description=(
        "Get available upcoming flights from the airport system database. "
        "Always use this tool when the user asks about available flights, "
        "scheduled flights, upcoming flights, departures, arrivals, routes, "
        "airlines, or airports. If the user does not provide filters, call it "
        "without filters and return general available flights."
    ),
    parameters={
        "type": "object",
        "properties": {
            "departure_city": {
                "type": "string",
                "description": "Departure city name, for example Berlin.",
            },
            "arrival_city": {
                "type": "string",
                "description": "Arrival city name, for example Munich.",
            },
            "departure_airport": {
                "type": "string",
                "description": "Departure airport name, for example Berlin Brandenburg Airport.",
            },
            "arrival_airport": {
                "type": "string",
                "description": "Arrival airport name, for example Munich Airport.",
            },
            "airline": {
                "type": "string",
                "description": "Airline name, for example Lufthansa.",
            },
            "flight_date": {
                "type": "string",
                "description": "Flight departure date in YYYY-MM-DD format.",
            },
            "status": {
                "type": "string",
                "description": "Flight status: scheduled, delayed, boarding, departed, arrived, cancelled.",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of flights to return.",
            },
        },
        "required": [],
    },
)


flight_details_tool = types.FunctionDeclaration(
    name="get_flight_details",
    description="Get detailed information about a specific flight by flight number.",
    parameters={
        "type": "object",
        "properties": {
            "flight_number": {
                "type": "string",
                "description": "Flight number, for example LH123.",
            },
        },
        "required": ["flight_number"],
    },
)

available_seats_tool = types.FunctionDeclaration(
    name="get_available_seats",
    description=(
        "Search available seats for a specific flight. "
        "Use this tool whenever the user asks about free seats, available seats, "
        "seat classes, seat prices, business seats, economy seats, window seats, "
        "aisle seats, exit row seats, or extra legroom seats for a flight. "
        "The flight_number is required. Other filters are optional."
    ),
    parameters={
        "type": "object",
        "properties": {
            "flight_number": {
                "type": "string",
                "description": "Flight number, for example LH123.",
            },
            "seat_class": {
                "type": "string",
                "description": "Optional seat class: economy, business, first, premium_economy.",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of seats to return.",
            },
        },
        "required": ["flight_number"],
    },
)


seat_details_tool = types.FunctionDeclaration(
    name="get_seat_details",
    description="Get details about a specific seat on a specific flight.",
    parameters={
        "type": "object",
        "properties": {
            "flight_number": {
                "type": "string",
                "description": "Flight number, for example LH123.",
            },
            "seat_number": {
                "type": "string",
                "description": "Seat number, for example 1A or 12C.",
            },
        },
        "required": ["flight_number", "seat_number"],
    },
)


ALL_TOOLS = [
    types.Tool(
        function_declarations=[
            available_flights_tool,
            flight_details_tool,
            available_seats_tool,
            seat_details_tool,
        ]
    )
]


def execute_tool(name: str, args: dict):
    if name == "get_available_flights":
        return get_available_flights(
            departure_city=args.get("departure_city"),
            arrival_city=args.get("arrival_city"),
            departure_airport=args.get("departure_airport"),
            arrival_airport=args.get("arrival_airport"),
            airline=args.get("airline"),
            flight_date=args.get("flight_date"),
            status=args.get("status"),
            limit=args.get("limit", 10),
        )

    if name == "get_flight_details":
        flight_number = args.get("flight_number")
        return get_flight_details(flight_number=flight_number)

    if name == "get_available_seats":
        return get_available_seats(
            flight_number=args.get("flight_number"),
            seat_class=args.get("seat_class"),
            limit=args.get("limit", 30),
        )

    if name == "get_seat_details":
        return get_seat_details(
            flight_number=args.get("flight_number"),
            seat_number=args.get("seat_number"),
        )

    raise ValueError(f"Unknown tool: {name}")



