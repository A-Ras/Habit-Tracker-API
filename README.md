# 🎯 Habit Tracker API

![CI](https://github.com/A-Ras/Habit-Tracker-API/actions/workflows/ci.yml/badge.svg)

Eine REST-API zur Verwaltung von Aufgaben, Projekten und Gewohnheiten — gebaut mit **FastAPI**, **SQLAlchemy** und **PostgreSQL**, vollständig dockerisiert und mit CI via GitHub Actions.

## ✨ Features

- 🔐 **JWT-Authentifizierung** (OAuth2 Password Flow, bcrypt-Hashing)
- 👤 **Benutzerverwaltung** (Registrierung, Profil)
- 📁 **Projekte** mit Besitzer-Zuordnung
- ✅ **Aufgaben** (To-Dos) inkl. Status-Filterung
- 🔥 **Gewohnheiten** (Habits) mit täglichen Check-Ins
- 🗄️ **Alembic-Migrationen** (versioniertes DB-Schema)
- 🐳 **Docker Compose** (API + PostgreSQL)
- ✅ **Testabdeckung** via pytest (13 Tests)

## 🛠️ Tech-Stack

| Bereich       | Technologie                                      |
|---------------|--------------------------------------------------|
| Framework     | FastAPI, Uvicorn                                 |
| Datenbank     | PostgreSQL 16 (lokal: SQLite-Fallback)           |
| ORM           | SQLAlchemy 2.0                                   |
| Migrationen   | Alembic                                          |
| Auth          | python-jose (JWT), bcrypt                        |
| Paket-Manager | [uv](https://docs.astral.sh/uv/)                 |
| Tests         | pytest                                           |
| CI            | GitHub Actions (Tests + Docker-Build)            |

## 🚀 Schnellstart (mit Docker)

Voraussetzung: [Docker](https://docs.docker.com/get-docker/) installiert.

```bash
git clone https://github.com/A-Ras/Habit-Tracker-API.git
cd Habit-Tracker-API
docker compose up -d --build
```

Danach läuft:

| Dienst      | URL                              |
|-------------|----------------------------------|
| API         | http://localhost:8000            |
| Swagger UI  | http://localhost:8000/docs       |
| PostgreSQL  | `localhost:5433` (Host-Port)     |

Beim Start des API-Containers werden automatisch die **Alembic-Migrationen** ausgeführt.

## 💻 Lokale Entwicklung (ohne Docker)

Voraussetzung: Python **3.14** und [uv](https://docs.astral.sh/uv/).

```bash
uv sync                    # Dependencies installieren
uv run uvicorn app.main:app --reload   # Dev-Server starten
```

Ohne `DATABASE_URL` wird automatisch ein SQLite-Fallback (`db/habit_tracker.db`) verwendet.

### Umgebungsvariablen (`.env`)

Eine `.env`-Datei im Projektroot anlegen (wird **nicht** committet):

```env
SECRET_KEY=ein-langer-zufaelliger-schluessel
DATABASE_URL=postgresql://habituser:habitpass@localhost:5433/habittracker
```

## 🗃️ Datenbank-Migrationen

```bash
# Schema-Änderungen nach Modell-Anpassungen autogenerieren
uv run python -m alembic revision --autogenerate -m "beschreibung"

# Migrationen anwenden
uv run python -m alembic upgrade head

# Migrationsstand prüfen
uv run python -m alembic current
```

> ⚠️ Schema-Änderungen laufen **ausschließlich über Alembic** — kein `create_all()` im App-Code.

## 🔌 Endpunkte (Überblick)

| Methode | Pfad                          | Beschreibung                     | Auth |
|---------|-------------------------------|----------------------------------|------|
| POST    | `/auth/login`                 | Login (JWT-Token)                | –    |
| POST    | `/users/`                     | Benutzer registrieren            | –    |
| GET     | `/users/me`                   | Eigenes Profil                   | ✅   |
| POST    | `/projects/`                  | Projekt anlegen                  | ✅   |
| GET     | `/projects/`                  | Eigene Projekte listen           | ✅   |
| GET     | `/projects/{id}/full`         | Projekt inkl. Aufgaben           | ✅   |
| POST    | `/tasks/`                     | Aufgabe anlegen                  | ✅   |
| GET     | `/tasks/`                     | Aufgaben listen (Status-Filter)  | ✅   |
| DELETE  | `/tasks/{id}`                 | Aufgabe löschen                  | ✅   |
| POST    | `/habits/`                    | Gewohnheit anlegen               | ✅   |
| POST    | `/habits/{id}/checkins`       | Check-In für heute               | ✅   |
| GET     | `/habits/{id}/checkins`       | Check-In-Historie                | ✅   |
| GET     | `/health`                     | Health-Check                     | –    |

Vollständige, interaktive Doku: **http://localhost:8000/docs**

## 🧪 Tests

```bash
uv run pytest
```

Die Tests laufen gegen eine isolierte SQLite-Testdatenbank (`test.db`) — kein PostgreSQL nötig.

## 🔄 CI / CD

GitHub Actions (`.github/workflows/ci.yml`), ausgelöst bei jedem `push` auf `main` und für Pull Requests:

1. **Tests** — Dependencies via `uv sync --frozen`, dann `uv run pytest`
2. **Docker-Build** — validiert, dass das Docker-Image baut

## 📁 Projektstruktur

```
├── app/
│   ├── main.py            # FastAPI-App & Router-Registrierung
│   ├── config.py          # Settings (pydantic-settings, .env)
│   ├── database.py        # Engine/Session (DATABASE_URL)
│   ├── models.py          # SQLAlchemy-Modelle
│   ├── schemas.py         # Pydantic-Schemas
│   ├── auth.py            # JWT & Passwort-Verifizierung
│   ├── crud.py            # DB-Operationen
│   └── routers/           # auth, users, projects, tasks, habits
├── alembic/               # Migrationsumgebung + versions/
├── tests/                 # pytest-Suite
├── src/habit_tracker_api/ # Paket-Stub (uv-Build-Backend)
├── docker-compose.yml     # api + db (Port 5433 → 5432)
├── Dockerfile             # uv-basiertes Produktionsimage
└── .github/workflows/     # CI (Tests + Docker-Build)
```


