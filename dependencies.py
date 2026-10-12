from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

from auth import SECRET_KEY, ALGORITHM

from jose import jwt


# Get token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    print("TOKEN RECEIVED:", token)

    try:

        # Decode JWT
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        print("TOKEN DATA:", payload)

        # Get user ID
        user_id = payload.get("user_id")

        if user_id is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except Exception as e:

        print("TOKEN ERROR:", e)

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    # Find user
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

def require_role(required_role):

    def role_checker(
        current_user = Depends(get_current_user)
    ):

        if current_user.role != required_role:

            raise HTTPException(
                status_code=403,
                detail="You don't have permission to access this area"
            )

        return current_user

    return role_checker

def require_permission(required_permission):

    def permission_checker(
        current_user = Depends(get_current_user)
    ):

        # Permissions for each role
        permissions = {

            "buyer": [
                "VIEW_PRODUCT",
                "MANAGE_CART",
                "CREATE_ORDER",
                "VIEW_ORDER"
            ],

            "seller": [
                "VIEW_PRODUCT",
                "CREATE_PRODUCT",
                "UPDATE_PRODUCT",
                "DELETE_PRODUCT",
                "VIEW_SELLER_ORDER"
            ],

            "admin": [
                "VIEW_PRODUCT",
                "CREATE_PRODUCT",
                "UPDATE_PRODUCT",
                "DELETE_PRODUCT",
                "MANAGE_USERS",
                "MANAGE_ORDERS",
                "MANAGE_PROMOTIONS",
                "MANAGE_PAYMENTS"
            ]
        }

        # Get permissions of current user's role
        user_permissions = permissions.get(
            current_user.role,
            []
        )

        # Check permission
        if required_permission not in user_permissions:

            raise HTTPException(
                status_code=403,
                detail="You don't have this permission"
            )

        return current_user

    return permission_checker