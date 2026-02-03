FROM python:3.11-slim

WORKDIR /app

# Install SDK first (server depends on it)
COPY sdk/ /app/sdk/
RUN pip install --no-cache-dir /app/sdk/

# Install server
COPY server/ /app/server/
RUN pip install --no-cache-dir /app/server/

EXPOSE 8000

CMD ["uvicorn", "vigil_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
