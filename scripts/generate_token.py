import sys
from pathlib import Path

# Add src folder to path so we can import auth
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from core.auth import create_jwt_token

if __name__ == "__main__":
    # Sample user data for token
    user_data = {"user_id": 1, "username": "testuser"}

    # Generate JWT token (expires in 1 hour by default)
    token = create_jwt_token(user_data)

    print("Generated JWT Token:")
    print(token)
