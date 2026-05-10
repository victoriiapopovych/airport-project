# Airport API

REST API for airport and flight management system built with Django REST Framework.

## Features

- Custom user system based on `AbstractUser`
- Airlines and airplanes management
- Airports, countries, and routes
- Flights scheduling system
- Ticket booking system
- Lounge and lounge access management
- Admin panel customization
- Swagger/OpenAPI documentation

---

## Tech Stack

- Python 3.11
- Django
- Django REST Framework
- PostgreSQL
- drf-spectacular
- PgAdmin

---

## Project Structure

### User App
- Custom User model
- Roles system (`admin`, `user`)
- Passport and citizenship information

### Location App
- Country
- City
- Airport

### Airline App
- Airline
- AirplaneType
- Airplane

### Flight App
- Route
- Flight

### Ticket App
- TicketClass
- Booking
- Ticket

### Lounge App
- Lounge
- LoungeAccess

---

## API Documentation

Swagger documentation:

```text
http://127.0.0.1:8000/api/docs/