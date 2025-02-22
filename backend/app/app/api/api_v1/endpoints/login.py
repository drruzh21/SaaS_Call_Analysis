from typing import Annotated, Any, Union

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.utilities import send_magic_login_email, send_reset_password_email

router = APIRouter()

"""
https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Authentication_Cheat_Sheet.md
Specifies minimum criteria:
    - Change password must require current password verification to ensure that it's the legitimate user.
    - Login page and all subsequent authenticated pages must be exclusively accessed over TLS or other strong transport.
    - An application should respond with a generic error message regardless of whether:
        - The user ID or password was incorrect.
        - The account does not exist.
        - The account is locked or disabled.
    - Code should go through the same process, no matter what, allowing the application to return in approximately
      the same response time.
    - In the words of George Orwell, break these rules sooner than do something truly barbaric.

See `security.py` for other requirements.
"""


@router.post("/magic/{email}", response_model=schemas.WebToken)
async def login_with_magic_link(*, db: Annotated[AsyncSession, Depends(deps.get_db)], email: str) -> Any:
    """
    First step of magic link login. Checks if user exists and generates magic link.
    Creates user if they don't exist.
    """
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        user_in = schemas.UserCreate(**{"email": email})
        user = await crud.user.create(db, obj_in=user_in)
    is_active = await crud.user.is_active(user)
    if not is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A link to activate your account has been emailed.")
    tokens = security.create_magic_tokens(subject=user.id)
    if settings.emails_enabled and user.email:
        await send_magic_login_email(email_to=user.email, token=tokens[0])
    return {"claim": tokens[1]}


@router.post("/claim", response_model=schemas.Token)
async def validate_magic_link(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    obj_in: schemas.WebToken,
    magic_in: Annotated[bool, Depends(deps.get_magic_token)],
) -> Any:
    """
    Second step of magic link login.
    """
    claim_in = deps.get_magic_token(token=obj_in.claim)
    user = await crud.user.get(db, id=magic_in.sub)
    if (
        (claim_in.sub != magic_in.sub)
        or (claim_in.fingerprint != magic_in.fingerprint)
        or not user
        or not await crud.user.is_active(user)
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login failed; invalid claim.")
    if not user.email_validated:
        await crud.user.validate_email(db=db, db_obj=user)
    refresh_token = None
    force_totp = True
    if not user.totp_secret:
        force_totp = False
        refresh_token = security.create_refresh_token(subject=user.id)
        await crud.token.create(db=db, obj_in=refresh_token, user_obj=user)
    return {
        "access_token": security.create_access_token(subject=user.id, force_totp=force_totp),
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/oauth", response_model=schemas.Token)
async def login_with_oauth2(
    db: Annotated[AsyncSession, Depends(deps.get_db)], 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Any:
    """
    First step of OAuth2 login.
    """
    user = await crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    if not form_data.password or not user or not await crud.user.is_active(user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login failed; incorrect email or password")
    refresh_token = None
    force_totp = True
    if not user.totp_secret:
        force_totp = False
        refresh_token = security.create_refresh_token(subject=user.id)
        await crud.token.create(db=db, obj_in=refresh_token, user_obj=user)
    return {
        "access_token": security.create_access_token(subject=user.id, force_totp=force_totp),
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/totp", response_model=schemas.Token)
async def login_with_totp(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    totp_data: schemas.WebToken,
    current_user: Annotated[models.User, Depends(deps.get_totp_user)],
) -> Any:
    """
    Final step of TOTP validation.
    """
    new_counter = security.verify_totp(
        token=totp_data.claim, secret=current_user.totp_secret, last_counter=current_user.totp_counter
    )
    if not new_counter:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login failed; unable to verify TOTP.")
    current_user = await crud.user.update_totp_counter(db=db, db_obj=current_user, new_counter=new_counter)
    refresh_token = security.create_refresh_token(subject=current_user.id)
    await crud.token.create(db=db, obj_in=refresh_token, user_obj=current_user)
    return {
        "access_token": security.create_access_token(subject=current_user.id),
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.put("/totp", response_model=schemas.Msg)
async def enable_totp_authentication(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    data_in: schemas.EnableTOTP,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    """
    Token validation before enabling TOTP.
    """
    if current_user.hashed_password:
        user = await crud.user.authenticate(db, email=current_user.email, password=data_in.password)
        if not data_in.password or not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to authenticate or activate TOTP.")
    totp_in = security.create_new_totp(label=current_user.email, uri=data_in.uri)
    new_counter = security.verify_totp(
        token=data_in.claim, secret=totp_in.secret, last_counter=current_user.totp_counter
    )
    if not new_counter:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to authenticate or activate TOTP.")
    current_user = await crud.user.activate_totp(db=db, db_obj=current_user, totp_in=totp_in)
    current_user = await crud.user.update_totp_counter(db=db, db_obj=current_user, new_counter=new_counter)
    return {"msg": "TOTP enabled. Do not lose your recovery code."}


@router.delete("/totp", response_model=schemas.Msg)
async def disable_totp_authentication(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    data_in: schemas.UserUpdate,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    """
    Disabling TOTP.
    """
    if current_user.hashed_password:
        user = await crud.user.authenticate(db, email=current_user.email, password=data_in.original)
        if not data_in.original or not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to authenticate or deactivate TOTP.")
    await crud.user.deactivate_totp(db=db, db_obj=current_user)
    return {"msg": "TOTP disabled."}


@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[models.User, Depends(deps.get_refresh_user)],
) -> Any:
    """
    Token refresh for future requests.
    """
    refresh_token = security.create_refresh_token(subject=current_user.id)
    await crud.token.create(db=db, obj_in=refresh_token, user_obj=current_user)
    return {
        "access_token": security.create_access_token(subject=current_user.id),
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/revoke", response_model=schemas.Msg)
async def revoke_token(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[models.User, Depends(deps.get_refresh_user)],
) -> Any:
    """
    Revoke refresh token
    """
    return {"msg": "Token revoked"}


@router.post("/recover/{email}", response_model=Union[schemas.WebToken, schemas.Msg])
async def recover_password(
    email: str, 
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> Any:
    """
    Password recovery
    """
    user = await crud.user.get_by_email(db, email=email)
    if user and await crud.user.is_active(user):
        tokens = security.create_magic_tokens(subject=user.id)
        if settings.emails_enabled:
            await send_reset_password_email(email_to=user.email, email=email, token=tokens[0])
            return {"claim": tokens[1]}
    return {"msg": "If such user exists, we will send you an email to reset your password."}


@router.post("/reset", response_model=schemas.Msg)
async def reset_password(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    new_password: str = Body(...),
    claim: str = Body(...),
    magic_in: Annotated[bool, Depends(deps.get_magic_token)],
) -> Any:
    """
    Reset password
    """
    claim_in = deps.get_magic_token(token=claim)
    # Get user
    user = await crud.user.get(db, id=magic_in.sub)
    # Validate claims
    if (
        (claim_in.sub != magic_in.sub)
        or (claim_in.fingerprint != magic_in.fingerprint)
        or not user
        or not await crud.user.is_active(user)
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update password: invalid claim.")
    # Update password
    hashed_password = security.get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    await db.commit()
    return {"msg": "Password successfully updated."}
