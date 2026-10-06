# ═══════════════════════════════════════════════════════════════
# Stage 1: Builder (schlankes Python-Image mit uv)
# ═══════════════════════════════════════════════════════════════
FROM python:3.12-slim-bookworm

# uv installieren (von Astral)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Arbeitsverzeichnis
WORKDIR /app

# Nur Dependency-Dateien zuerst kopieren (für Docker-Layer-Caching)
COPY pyproject.toml uv.lock ./

# Dependencies installieren (ohne Projekt-Code)
RUN uv sync --frozen --no-install-project

# Jetzt den restlichen Code kopieren
COPY . .

# Projekt selbst installieren
RUN uv sync --frozen

# Port freigeben
EXPOSE 8000

# WICHTIG: --host 0.0.0.0, sonst ist der Container von außen nicht erreichbar!
CMD ["uv", "run", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]