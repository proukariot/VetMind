# How to Run the Server with Docker

This guide explains how to build and run the FastAPI server inside Docker.

---

## 1. Create a `.env` file

Example dummy `.env`:

```
OPENAI_API_KEY=sk-test-123456
MODEL=gpt-4.1
SUPABASE_URL=https://dummy-project.supabase.co
SUPABASE_KEY=dummy-service-role-key-123
```

Place this file next to the `Dockerfile`.

---

## 2. Build the Docker image

Run in the terminal inside the project folder:

```bash
docker build -f server/Dockerfile -t pet-extractor . 
# docker build -t pet-extractor .
```

---

## 3. Run the container

```bash
docker run -p 8000:8000 --env-file .env pet-extractor
```

The server will be available at:

```
http://localhost:8000
```

---

## 4. Test the server

```bash
curl http://localhost:8000/
```

---

## 5. Stop the container

To stop manually:

```bash
docker ps
docker stop <container_id>
```

To stop interactive mode, press:

```
CTRL + C
```

---

## 6. Optional: run in background

```bash
docker run -d -p 8000:8000 --env-file .env pet-extractor
```

---

You're all set 🚀
