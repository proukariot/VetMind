FROM python:3.11-slim

WORKDIR /app

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY llm/ llm/
COPY server/ server/
COPY schemas/ schemas/
COPY .env .


# Expose FastAPI port
EXPOSE 8000

# Run server
CMD ["uvicorn", "server.server:app", "--host", "0.0.0.0", "--port", "8000"]