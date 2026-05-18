# 1. Clone the repo
git clone repo
cd studybuddy

# 2. Copy env template and fill in your values
cp .env.example .env
# Edit .env with your credentials

# 3. Build and start all services
docker compose up --build

# 4. Run database migrations (in a second terminal)
docker compose exec backend alembic upgrade head

# 5. Verify all services are healthy
docker compose ps

# ── Daily use ────────────────────────────────────
# Start services (no rebuild)
docker compose up

# Stop services (preserves data volumes)
docker compose down

# Stop and wipe all data (fresh start)
docker compose down -v

# Tail logs for one service
docker compose logs -f backend

# Open a shell inside a container
docker compose exec backend bash
docker compose exec postgres psql -U studybuddy -d studybuddy_db