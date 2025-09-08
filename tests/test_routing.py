"""
This module contains a simple FastAPI application for testing routing and header propagation.

It includes endpoints to:
- Get a list of users.
- Create a new user.
- Echo back specific headers to test middleware functionality.
"""
from fastapi import FastAPI, Request

# Initialize the FastAPI application.
app = FastAPI()

@app.get("/users")
async def get_users():
    """
    Retrieves a static list of users.

    This is a simple GET endpoint to test basic routing.

    Returns:
        dict: A dictionary containing a list of user names.
    """
    return {"users": ["Alice", "Bob", "Charlie"]}

@app.post("/users")
async def create_user(user: dict):
    """
    Accepts and creates a new user.

    This POST endpoint demonstrates handling a JSON payload.

    Args:
        user (dict): A dictionary representing the user data.

    Returns:
        dict: A confirmation message and the user data that was received.
    """
    return {"message": "User created", "user": user}

@app.get("/whoami")
async def whoami(request: Request):
    """
    Echoes back specific headers from the request.

    This endpoint is designed to test if middleware, such as an
    authentication or header-passing middleware, is correctly
    propagating headers like 'x-user-id' and 'x-username'.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        dict: A dictionary containing the received headers.
    """
    return {
        "received_headers": {
            "x-user-id": request.headers.get("x-user-id"),
            "x-username": request.headers.get("x-username")
        }
    }
