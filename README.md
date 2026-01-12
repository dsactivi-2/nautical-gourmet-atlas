# Nautical Gourmet Atlas

A mobile-first application for discovering premium partners, discounts, and local treasures along the Croatian coast.

## Features

- **Map-based Discovery**: Find partners using an interactive map with BBOX queries
- **Categories & Filters**: Browse by category (Premium Partners, Nautical Foodie, Liquid Treasures, etc.)
- **Premium Discounts**: PIN-based discount redemption system
- **Favorites**: Save your favorite partners
- **Visit History**: Track your visits and discount usage
- **Treasures**: Discover local wines, traditional dishes, products, and crafts
- **Multi-language**: HR/EN/DE support via Accept-Language header

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL + PostGIS** - Spatial database
- **SQLAlchemy** - ORM with async support
- **JWT Auth** - Access & refresh tokens
- **Pydantic** - Data validation

### Mobile (Frontend)
- **Expo** - React Native development platform
- **TypeScript** - Type safety
- **Expo Router** - File-based navigation
- **TanStack Query** - Data fetching & caching
- **Zustand** - State management
- **i18next** - Internationalization

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Backend Setup

```bash
cd backend

# Start PostgreSQL with PostGIS
docker compose up -d db

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Initialize database
python -m app.scripts.init_db

# Seed demo data
python -m app.scripts.seed_demo

# Run API server
uvicorn app.main:app --reload --port 8000
```

API will be available at http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Mobile Setup

```bash
cd mobile

# Install dependencies
npm install

# Start Expo dev server
npx expo start
```

Scan the QR code with Expo Go app or press:
- `i` for iOS simulator
- `a` for Android emulator

### Environment Variables

Backend (`.env`):
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/nautical_gourmet
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/nautical_gourmet
JWT_SECRET=your-secret-key-change-in-production
```

Mobile (`app.json` > `extra`):
```json
{
  "apiBaseUrl": "http://localhost:8000/v1"
}
```

## API Endpoints

### Auth
- `POST /v1/auth/register` - Register new user
- `POST /v1/auth/login` - Login
- `POST /v1/auth/refresh` - Refresh token

### User
- `GET /v1/me` - Get current user
- `PATCH /v1/me` - Update user profile

### Categories & Filters
- `GET /v1/categories` - List categories
- `GET /v1/filters` - List filters (optional: `?category_id=`)

### Partners
- `GET /v1/partners` - List partners with filters
  - `?bbox=minLng,minLat,maxLng,maxLat`
  - `?category_id=`
  - `?filter_ids=1,2,3`
  - `?q=search`
  - `?premium_only=true`
- `GET /v1/partners/{id}` - Partner details (includes PIN for auth users)

### Favorites
- `GET /v1/favorites` - List favorites
- `POST /v1/favorites` - Add favorite
- `DELETE /v1/favorites/{id}` - Remove favorite

### Visits
- `GET /v1/visits` - List visits
- `POST /v1/visits` - Create visit
- `PATCH /v1/visits/{id}` - Update visit (mark discount used)

### Treasures
- `GET /v1/treasures` - List treasures
- `GET /v1/treasures/categories` - List treasure categories
- `GET /v1/treasures/{id}` - Treasure details

## Project Structure

```
nautical-gourmet-atlas/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Auth, language services
│   │   ├── scripts/      # DB init & seed
│   │   ├── config.py     # Settings
│   │   ├── database.py   # DB connection
│   │   └── main.py       # FastAPI app
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── requirements.txt
│
├── mobile/
│   ├── app/              # Expo Router screens
│   │   ├── (auth)/       # Auth screens
│   │   ├── (tabs)/       # Tab screens
│   │   ├── partner/      # Partner detail
│   │   └── treasure/     # Treasure detail
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── components/   # UI components
│   │   ├── hooks/        # State stores
│   │   ├── i18n/         # Translations
│   │   └── types/        # TypeScript types
│   ├── app.json
│   ├── package.json
│   └── tsconfig.json
│
└── README.md
```

## Demo Data

The seed script creates:
- 6 Categories (Premium Partners, Nautical Foodie, etc.)
- 9 Filters (Seafood, Wine, Cheese, etc.)
- 5 Partners (Konoba Mate, Bibich Winery, Gligora Cheese, etc.)
- 4 Treasures (Plavac Mali, Paški Sir, Dalmatian Pršut, Pag Lace)

## License

MIT
