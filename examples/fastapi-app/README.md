# FastAPI Example Project

This is a simple FastAPI example project that demonstrates how to use WUP with a FastAPI application.

## Structure

```
.
├── app/
│   ├── __init__.py
│   └── users/
│       ├── __init__.py
│       └── routes.py
├── main.py
├── Dockerfile
├── requirements.txt
└── wup.yaml
```

## Running with Docker

```bash
# Build the image
docker build -t fastapi-example .

# Run the container
docker run -p 8000:8000 fastapi-example
```

## Using WUP

```bash
# Initialize WUP config
wup init

# Build dependency map
wup map-deps .

# Start watching
wup watch
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /users/` - List users
- `GET /users/{user_id}` - Get user by ID
- `POST /users/` - Create user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user
