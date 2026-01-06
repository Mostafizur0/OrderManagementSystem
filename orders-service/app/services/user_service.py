import httpx
from fastapi import HTTPException, status
from app.core.settings import settings


async def verify_user_exists(user_id: int, token: str) -> bool:
    """
    Verify that a user exists in the users-service
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.USERS_SERVICE_URL}/v1/auth/me",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                user_data = response.json()
                # Verify the returned user ID matches the token's user ID
                return str(user_data.get("id")) == str(user_id)
            elif response.status_code == 404:
                return False
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Users service unavailable"
                )
                
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to connect to users service"
        )
