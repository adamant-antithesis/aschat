import logging
import httpx
from fastapi import HTTPException


async def get_user_from_django(token: str):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    logging.info(f"Decoding token...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                # "http://django:8000/api/user/",
                "https://44a2-188-163-20-93.ngrok-free.app/api/user/",
                headers={"Authorization": f"Bearer {token}"}
            )

        logging.info(f"Received response from Django. Status code: {response.status_code}")

        if response.status_code != 200:
            logging.error(f"Failed to retrieve user data. Status code: {response.status_code}, Response: {response.text}")
            raise HTTPException(status_code=401, detail="User not found in Django system")

        user_data = response.json()

        logging.info(f"User data retrieved: {user_data}")

        return user_data

    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error occurred: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        raise credentials_exception
