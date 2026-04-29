# Flask Example Project

This is a simple Flask example project that demonstrates how to use WUP with a Flask application.

## Structure

```
.
├── app/
│   ├── __init__.py
│   └── auth/
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
docker build -t flask-example .

# Run the container
docker run -p 5000:5000 flask-example
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
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout
- `POST /auth/register` - Register
- `GET /auth/profile` - Get profile
- `PUT /auth/password` - Change password
