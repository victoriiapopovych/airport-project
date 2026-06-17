# ✈️ Airport Management API

REST API for airport and flight management system built with **Django REST Framework**.

## 🚀 Features

* 🔐 JWT Authentication
* 👥 Role-Based Access Control
* 🌍 Countries, Cities, and Airports Management
* 🛫 Airlines, Airplanes, and Airplane Types Management
* 💺 Automatic Airplane Seat Generation
* 🗺️ Routes and Flight Scheduling
* 🎫 Flight Booking System
* ⏳ Temporary Seat Reservation Logic
* 🏢 Lounge Management and Access Control
* 📄 Pagination, Filtering, and Search
* 📖 Swagger/OpenAPI Documentation
* 🐳 Docker Support
* 📧 Email Notifications
* 📝 Activity Logging

---

## 🛠️ Tech Stack

* 🐍 Python 3.11
* 🌐 Django
* 🔧 Django REST Framework
* 🐘 PostgreSQL
* 🔐 JWT Authentication
* 📖 drf-spectacular (Swagger/OpenAPI)
* 🐳 Docker & Docker Compose
* 📬 SMTP Email Service
* 🗄️ PgAdmin

---

## 🏗️ Project Structure

### 👤 Users App

* Custom User model
* Role-based permissions:

  * Passenger
  * Support
  * Manager
  * Lounge Operator
* Passport and citizenship information
* User verification support

### 🌍 Location App

* Countries
* Cities
* Airports

### 🛫 Airline App

* Airlines
* Airplane Types
* Airplanes
* Seat Classes
* Airplane Seats
* Automatic seat generation

### ✈️ Flight App

* Routes
* Flights
* Flight Seats
* Flight status management
* Dynamic ticket pricing based on seat class

### 🎫 Tickets App

* Bookings
* Tickets
* Seat reservation system
* Booking status management
* Automatic booking expiration logic

### 🏢 Services App

* Lounges
* Lounge Access
* Capacity validation
* Working hours validation

---

## 🔒 User Roles

| Role               | Permissions                                     |
| ------------------ | ----------------------------------------------- |
| 👤 Passenger       | Book flights and manage own bookings            |
| 🎧 Support         | Manage booking statuses                         |
| 🧑‍💼 Manager      | Manage airlines, airplanes, routes, and flights |
| 🏢 Lounge Operator | Manage lounges and lounge access                |
| 👑 Admin           | Full system access                              |

---

## 📖 API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/api/docs/
```

OpenAPI Schema:

```text
http://127.0.0.1:8000/api/schema/
```

---

## 🐳 Running with Docker

Build and start containers:

```bash
docker compose up --build
```

Run in detached mode:

```bash
docker compose up -d
```

Stop containers:

```bash
docker compose down
```

---

## 🎯 Main Business Logic

* 💺 Automatic airplane seat generation
* 🎫 Booking creation with seat reservation
* ⏳ Reservation expiration handling
* 💰 Dynamic ticket pricing
* 🏢 Lounge access validation
* 👥 Role-based permissions
* ✈️ Automatic flight seat creation
* 📧 Email notification support

---

## 📌 Status

🚧 The project is actively developed as part of a backend internship program and is continuously extended with new features and integrations.
