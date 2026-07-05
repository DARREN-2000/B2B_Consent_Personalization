# Installation Guide

ConsentHub provides Docker and Kubernetes-based installation pathways.

## Docker Setup

### 1. Requirements
Ensure Docker and Docker Compose (v2) are installed.

### 2. Configure Environment
```bash
cp .env.example .env
```
Populate `.env` with secure credentials:
```env
SECRET_KEY=generate_a_random_32_char_string
JWT_SECRET_KEY=generate_another_random_string
ADMIN_API_KEY=your_secure_admin_key
POSTGRES_PASSWORD=secure_database_password
```

### 3. Build & Run
```bash
docker-compose up --build -d
```
The backend API is now running on `http://localhost:5000` and the frontend UI on `http://localhost:3000`.

## Kubernetes Setup

See the [Deployment](deployment.md) guide for comprehensive Helm chart instructions.