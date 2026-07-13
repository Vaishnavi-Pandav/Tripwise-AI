# TripWise AI ✈️

> An AI-powered travel planning platform built with FastAPI, React, and Google Gemini.

[![Live Frontend](https://img.shields.io/badge/Frontend-Vercel-black?logo=vercel)](https://tripwise-ai.vercel.app)
[![Live Backend](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render)](https://tripwise-ai-backend.onrender.com/docs)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [AI Orchestrator](#ai-orchestrator)
- [Deployment](#deployment)
- [Screenshots](#screenshots)

---

## Overview

TripWise AI is a full-stack travel planning application that helps users plan trips using a conversational AI assistant powered by Google Gemini. Users can generate detailed itineraries, compare destinations, find hotels, check live weather, calculate routes, and blog about their travel experiences — all in one place.

---

## Features

### AI & Intelligence
- **AI Chat** — conversational travel assistant powered by Google Gemini Flash Lite
- **LangChain-style Orchestrator** — conversation memory (last 5 exchanges), RAG from the database, and tool calling for weather/routes
- **RAG (Retrieval-Augmented Generation)** — AI searches hotels, destinations, and hidden gems from the database before answering
- **Tool Calling** — AI auto-fetches live weather and route data based on user intent
- **Itinerary Generator** — generates full day-by-day itineraries in Markdown with budget breakdown in ₹ INR
- **AI Budget Optimizer** — AI-powered cost-saving recommendations for trips

### Trip Planning
- Create and manage trips with source, destination, budget, days, travelers
- View trip history with status (planned / completed / cancelled / draft)
- Destination comparison across 8 factors (safety, food, adventure, etc.)
- Route calculator with car / bus / train / flight cost estimates in ₹
- Hidden gems finder for off-beat destinations
- Hotel recommendations scored by budget match and rating

### Dashboard & Analytics
- **4-tab dashboard**: My Trips · Analytics · Travel Blog · Map
- Analytics with 6 KPI cards and top destinations bar chart
- Interactive map showing all trip destinations (OpenStreetMap, no API key needed)
- Travel Blog — write, share, and delete experience posts (stored locally)

### Other
- Google Firebase Authentication (Google OAuth + Email/Password)
- Live weather data via OpenWeatherMap API
- Responsive design — works on mobile, tablet, and desktop
- Travel agencies directory (100+ agencies across all Indian states)
- PDF export for trip data
- Favorites and wishlist for hotels, destinations, packages
- Notifications system for travel alerts

---

## Tech Stack

### Frontend
| Tool | Version | Purpose |
|---|---|---|
| React | 19 | UI framework |
| TypeScript | 6 | Type safety |
| Vite | 8 | Build tool |
| Tailwind CSS | 4 | Styling |
| Framer Motion | 12 | Animations |
| Lucide React | latest | Icons |
| Axios | 1.x | HTTP client |
| Firebase | 12 | Authentication |
| Leaflet | 1.9 | Interactive maps |
| React Router | 7 | Client-side routing |

### Backend
| Tool | Version | Purpose |
|---|---|---|
| FastAPI | 0.111 | Web framework |
| Python | 3.11 | Runtime |
| SQLAlchemy | 2.0 | ORM |
| PostgreSQL | — | Production database (Supabase) |
| SQLite | — | Local development database |
| Alembic | 1.18 | Database migrations |
| google-genai | 2.8 | Gemini AI SDK |
| firebase-admin | 7.4 | Firebase token verification |
| psycopg2-binary | 2.9 | PostgreSQL driver |
| slowapi | 0.1.9 | Rate limiting |
| uvicorn | 0.30 | ASGI server |

### Infrastructure
| Service | Purpose |
|---|---|
| Vercel | Frontend hosting |
| Render | Backend hosting (Docker) |
| Supabase | PostgreSQL database |
| Firebase | Authentication |
| OpenWeatherMap | Weather API |
| Google AI Studio | Gemini API key |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                     │
│  React + TypeScript + Vite + Tailwind                   │
│  Firebase Auth → sends JWT token with every request     │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS + Bearer Token
┌───────────────────────▼─────────────────────────────────┐
│                  Backend (Render/Docker)                 │
│  FastAPI + Python 3.11                                  │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  AI Service │  │  21 API      │  │  Auth Service │  │
│  │  Orchestrat.│  │  Routers     │  │  Firebase JWT │  │
│  └──────┬──────┘  └──────┬───────┘  └───────────────┘  │
│         │                │                              │
│  ┌──────▼──────┐  ┌──────▼───────┐                     │
│  │  Gemini API │  │  SQLAlchemy  │                     │
│  │  (Google)   │  │  ORM         │                     │
│  └─────────────┘  └──────┬───────┘                     │
└──────────────────────────┼──────────────────────────────┘
                           │ postgresql+psycopg2
┌──────────────────────────▼──────────────────────────────┐
│              Supabase PostgreSQL (22 tables)             │
└─────────────────────────────────────────────────────────┘
```

### AI Orchestrator Flow

```
User message
     │
     ▼
1. Trip context injection (if trip_id provided)
     │
     ▼
2. Conversation memory (last 5 exchanges per user)
     │
     ▼
3. RAG — detect cities → search DB for hotels/destinations/gems
     │
     ▼
4. Tool calling — detect weather/route intent → call live APIs
     │
     ▼
5. Assemble full prompt → Gemini Flash Lite → reply
     │
     ▼
6. Save to memory + DB → return response
```

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Vaishnavi-Pandav/Tripwise-AI.git
cd Tripwise-AI
git checkout develop
```

### 2. Backend setup

```bash
cd Backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env file and fill in your values
cp .env.example .env
```

Edit `Backend/.env` with your keys (see [Environment Variables](#environment-variables)).

```bash
# Create SQLite tables for local dev (no Supabase needed locally)
python -c "from app.db.session import Base, engine; import app.models; Base.metadata.create_all(bind=engine); print('Tables created')"

# Start the backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs at: `http://localhost:8000`  
API docs at: `http://localhost:8000/docs`

### 3. Frontend setup

```bash
cd Frontend

# Install dependencies
npm install

# Copy env file
cp .env.example .env
```

Edit `Frontend/.env` with your Firebase keys (see [Environment Variables](#environment-variables)).

```bash
# Start the frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## Environment Variables

### Backend — `Backend/.env`

```env
# Gemini AI (get from https://aistudio.google.com)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=models/gemini-flash-lite-latest

# Database
# Local dev — SQLite (no setup needed):
DATABASE_URL=sqlite:///./tripwise.db
# Production — Supabase Session Pooler:
# DATABASE_URL=postgresql://postgres.YOUR_PROJECT:password@aws-0-ap-south-1.pooler.supabase.com:5432/postgres

# JWT
SECRET_KEY=your_secret_key_min_32_chars
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
FRONTEND_URL=http://localhost:5173

# Firebase (get from Firebase Console → Project Settings)
FIREBASE_PROJECT_ID=your_firebase_project_id

# Weather (get from https://openweathermap.org/api — free tier)
WEATHER_API_KEY=your_openweathermap_key

# Admin
ADMIN_SECRET=your_admin_secret
```

### Frontend — `Frontend/.env`

```env
# Backend API URL
VITE_API_URL=http://localhost:8000

# Firebase (get from Firebase Console → Project Settings → SDK config)
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

---

## Project Structure

```
Tripwise/
├── Backend/
│   ├── app/
│   │   ├── api/              # 21 FastAPI routers
│   │   │   ├── ai.py         # AI chat, generate, memory endpoints
│   │   │   ├── auth.py       # Firebase + JWT auth
│   │   │   ├── trips.py      # Trip CRUD
│   │   │   ├── hotels.py     # Hotel listing & recommendations
│   │   │   ├── weather.py    # Live weather (public)
│   │   │   ├── routes.py     # Route calculation
│   │   │   ├── comparison.py # Destination compare + public list
│   │   │   └── ...           # budget, packages, analytics, etc.
│   │   ├── core/
│   │   │   ├── config.py     # Settings & DB URL normalisation
│   │   │   ├── dependencies.py # Auth middleware (Firebase + JWT)
│   │   │   └── security.py   # JWT encode/decode, bcrypt
│   │   ├── db/
│   │   │   └── session.py    # SQLAlchemy engine + get_db()
│   │   ├── models/           # 21 SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── ai_service.py # LangChain-style orchestrator
│   │   │   ├── weather_service.py
│   │   │   ├── route_service.py
│   │   │   └── ...           # 18 other service modules
│   │   └── main.py           # FastAPI app factory + startup
│   ├── alembic/              # Database migration scripts
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
│
├── Frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   │   ├── Navbar.tsx    # Responsive navigation
│   │   │   ├── MapModal.tsx  # Leaflet map modal
│   │   │   ├── RouteMapModal.tsx
│   │   │   └── ...
│   │   ├── pages/
│   │   │   ├── Home.tsx      # Landing page
│   │   │   ├── Dashboard.tsx # Tabbed dashboard (trips/analytics/blog/map)
│   │   │   ├── Chat.tsx      # AI chat interface
│   │   │   ├── Results.tsx   # Trip planner + itinerary
│   │   │   ├── Profile.tsx   # User profile & settings
│   │   │   ├── Agencies.tsx  # Travel agencies directory
│   │   │   ├── Login.tsx
│   │   │   └── Signup.tsx
│   │   ├── services/
│   │   │   ├── api.ts        # Axios client + all API calls
│   │   │   └── firebase.ts   # Firebase auth setup
│   │   ├── context/
│   │   │   └── AuthContext.tsx
│   │   ├── data/
│   │   │   └── agencies.ts   # 100+ Indian travel agencies
│   │   ├── utils/
│   │   │   └── cityCoords.ts # City coordinate lookup
│   │   └── index.css         # Tailwind + custom utilities
│   ├── vercel.json
│   └── package.json
│
├── render.yaml               # Render deployment config
└── README.md
```

---

## API Reference

Base URL (production): `https://tripwise-ai-backend.onrender.com`  
Interactive docs: `https://tripwise-ai-backend.onrender.com/docs`

### Public endpoints (no auth required)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/api/v1/weather/{city}` | Live weather for a city |
| GET | `/api/v1/weather/forecast/{city}` | 7-day forecast |
| GET | `/api/v1/destinations/` | List destinations with filters |
| POST | `/api/v1/ai/chat` | Chat with AI (works unauth too) |
| POST | `/api/v1/ai/generate` | Generate itinerary |
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login with email/password |
| POST | `/api/v1/auth/firebase` | Login with Firebase token |

### Authenticated endpoints (Bearer token required)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/trips/` | List user's trips |
| POST | `/api/v1/trips/` | Create a trip |
| DELETE | `/api/v1/trips/{id}` | Delete a trip |
| GET | `/api/v1/hotels/` | Browse hotels |
| GET | `/api/v1/hotels/recommendations/{trip_id}` | AI hotel picks |
| POST | `/api/v1/routes/calculate` | Calculate route & costs |
| POST | `/api/v1/destinations/compare` | Compare two destinations |
| GET | `/api/v1/dashboard/analytics` | User analytics |
| GET | `/api/v1/ai/history` | Chat history |
| GET | `/api/v1/ai/memory` | Conversation memory |
| DELETE | `/api/v1/ai/memory` | Clear memory |

---

## AI Orchestrator

The AI service (`Backend/app/services/ai_service.py`) implements a LangChain-style orchestration pipeline without adding LangChain as a dependency (to avoid Docker build conflicts):

### Conversation Memory
- Sliding window of the last **5 exchanges** per user
- Stored in-process memory (`dict` keyed by `user_id`)
- Injected into every prompt automatically
- Clear via `DELETE /api/v1/ai/memory`

### RAG (Retrieval-Augmented Generation)
Before calling Gemini, the service queries the database based on detected intent:
- **Destinations** — when user asks "where to visit", "suggest places"
- **Hotels** — when user mentions "hotel", "stay", "accommodation"
- **Hidden gems** — when user asks for "offbeat", "hidden", "local spots"

### Tool Calling
Automatically invoked based on keywords in the message:
- **Weather tool** — triggered by: "weather", "temperature", "rain", "climate", "monsoon"
- **Route tool** — triggered by: "how to reach", "distance", "train", "flight", "route from X to Y"

City detection covers **50+ Indian cities** from the message text.

---

## Deployment

### Backend (Render)

1. Push code to `develop` branch on GitHub
2. Render auto-deploys via `render.yaml`
3. Set these env vars in Render dashboard:

| Key | Value |
|---|---|
| `DATABASE_URL` | Supabase Session Pooler URL (see note below) |
| `GEMINI_API_KEY` | Your Gemini API key |
| `SECRET_KEY` | Random 32+ char string |
| `FRONTEND_URL` | `https://tripwise-ai.vercel.app` |
| `FIREBASE_PROJECT_ID` | `your_firebase_project_id` |
| `WEATHER_API_KEY` | OpenWeatherMap key |
| `RUN_MIGRATIONS` | `true` |

> **Important:** Use the Supabase **Session Pooler** URL, not the direct connection string.  
> Format: `postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres`

### Frontend (Vercel)

1. Connect GitHub repo to Vercel
2. Set root directory to `Frontend`
3. Set these env vars in Vercel dashboard:

| Key | Value |
|---|---|
| `VITE_API_URL` | `https://tripwise-ai-backend.onrender.com` |
| `VITE_FIREBASE_API_KEY` | Firebase API key |
| `VITE_FIREBASE_AUTH_DOMAIN` | Firebase auth domain |
| `VITE_FIREBASE_PROJECT_ID` | Firebase project ID |
| `VITE_FIREBASE_STORAGE_BUCKET` | Firebase storage bucket |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | Firebase sender ID |
| `VITE_FIREBASE_APP_ID` | Firebase app ID |

### Firebase setup

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Enable **Authentication** → Sign-in methods → Google + Email/Password
3. Add your Vercel domain to **Authorized domains**

---

## Screenshots

| Page | Description |
|---|---|
| Home | Landing page with hero, features, destinations |
| AI Chat | Real-time chat with Gemini AI assistant |
| Trip Planner | Form → AI-generated itinerary with map |
| Dashboard | Trips, analytics charts, blog, map tabs |
| Agencies | 100+ travel agencies by state with filters |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Vaishnavi Pandav**  
Built with ❤️ using FastAPI, React, and Google Gemini AI
