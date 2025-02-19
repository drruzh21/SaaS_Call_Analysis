import logging
from typing import Any, Dict, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.constants import MAX_GPT_FILTER_PROMPT_LENGTH, MIN_GPT_FILTER_PROMPT_LENGTH
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.totp import NewTOTP
from app.schemas.user import UserCreate, UserInDB, UserUpdate

logger = logging.getLogger(__name__)


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model."""
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            db: Database session
            email: User's email address
            
        Returns:
            User object if found, None otherwise
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            obj_in: User creation data
            
        Returns:
            Created user object
        """
        # Используем exclude_none=True вместо exclude_unset=True,
        # чтобы включить все поля со значениями по умолчанию
        create_data = obj_in.model_dump(exclude_none=True)
        
        # Обрабатываем пароль
        if create_data.get("password"):
            create_data["hashed_password"] = get_password_hash(create_data["password"])
            del create_data["password"]
        
        # Устанавливаем значения по умолчанию для обязательных полей
        if "role" not in create_data:
            create_data["role"] = "user"
        if "balance_rub" not in create_data:
            create_data["balance_rub"] = 0
        if "email_validated" not in create_data:
            create_data["email_validated"] = False
        if "is_active" not in create_data:
            create_data["is_active"] = True
        if "is_superuser" not in create_data:
            create_data["is_superuser"] = False
            
        db_obj = User(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: User, 
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update a user.
        
        Args:
            db: Database session
            db_obj: Existing user object
            obj_in: User update data
            
        Returns:
            Updated user object
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        # Handle password update
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
            
        # Reset email validation if email changes
        if update_data.get("email") and db_obj.email != update_data["email"]:
            update_data["email_validated"] = False
            
        # Remove sensitive fields that shouldn't be updated directly
        sensitive_fields = {"id", "created", "modified"}
        for field in sensitive_fields:
            update_data.pop(field, None)
            
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user.
        
        Args:
            db: Database session
            email: User's email
            password: User's password
            
        Returns:
            Authenticated user object if successful, None otherwise
        """
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not user.hashed_password:
            return None
        if not verify_password(plain_password=password, hashed_password=user.hashed_password):
            return None
        return user

    async def validate_email(self, db: AsyncSession, *, db_obj: User) -> User:
        """
        Mark user's email as validated.
        
        Args:
            db: Database session
            db_obj: User object
            
        Returns:
            Updated user object
        """
        obj_in = UserUpdate(**UserInDB.model_validate(db_obj).model_dump())
        obj_in.email_validated = True
        return await self.update(db=db, db_obj=db_obj, obj_in=obj_in)

    async def activate_totp(self, db: AsyncSession, *, db_obj: User, totp_in: NewTOTP) -> User:
        """
        Activate TOTP for a user.
        
        Args:
            db: Database session
            db_obj: User object
            totp_in: TOTP configuration
            
        Returns:
            Updated user object
        """
        obj_in = UserUpdate(**UserInDB.model_validate(db_obj).model_dump())
        update_data = obj_in.model_dump(exclude_unset=True)
        update_data["totp_secret"] = totp_in.secret
        return await self.update(db=db, db_obj=db_obj, obj_in=update_data)

    async def deactivate_totp(self, db: AsyncSession, *, db_obj: User) -> User:
        """
        Deactivate TOTP for a user.
        
        Args:
            db: Database session
            db_obj: User object
            
        Returns:
            Updated user object
        """
        obj_in = UserUpdate(**UserInDB.model_validate(db_obj).model_dump())
        update_data = obj_in.model_dump(exclude_unset=True)
        update_data.update({
            "totp_secret": None,
            "totp_counter": None
        })
        return await self.update(db=db, db_obj=db_obj, obj_in=update_data)

    async def update_totp_counter(self, db: AsyncSession, *, db_obj: User, new_counter: int) -> User:
        """
        Update TOTP counter for a user.
        
        Args:
            db: Database session
            db_obj: User object
            new_counter: New TOTP counter value
            
        Returns:
            Updated user object
        """
        obj_in = UserUpdate(**UserInDB.model_validate(db_obj).model_dump())
        update_data = obj_in.model_dump(exclude_unset=True)
        update_data["totp_counter"] = new_counter
        return await self.update(db=db, db_obj=db_obj, obj_in=update_data)

    async def toggle_user_state(self, db: AsyncSession, *, obj_in: Union[UserUpdate, Dict[str, Any]]) -> Optional[User]:
        """
        Toggle user's active state.
        
        Args:
            db: Database session
            obj_in: Update data containing email and new state
            
        Returns:
            Updated user object if found, None otherwise
        """
        db_obj = await self.get_by_email(db, email=obj_in.email)
        if not db_obj:
            return None
        return await self.update(db=db, db_obj=db_obj, obj_in=obj_in)

    async def update_gpt_filter_prompt(
        self,
        db: AsyncSession,
        *,
        user_id: Any,
        gpt_filter_prompt: str
    ) -> Optional[User]:
        """
        Updates user's GPT filter prompt with length validation.
        
        Args:
            db: Async database session
            user_id: User's UUID
            gpt_filter_prompt: New prompt text
            
        Returns:
            Updated User object or None if not found
        """
        if len(gpt_filter_prompt) < MIN_GPT_FILTER_PROMPT_LENGTH:
            raise ValueError(f"Prompt too short (min {MIN_GPT_FILTER_PROMPT_LENGTH} chars)")
        if len(gpt_filter_prompt) > MAX_GPT_FILTER_PROMPT_LENGTH:
            raise ValueError(f"Prompt too long (max {MAX_GPT_FILTER_PROMPT_LENGTH} chars)")
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        
        if not user:
            logger.error(f"User {user_id} not found for prompt update")
            return None
            
        user.gpt_filter_prompt = gpt_filter_prompt
        await db.commit()
        await db.refresh(user)
        logger.info(f"Updated GPT filter prompt for user {user_id}")
        return user

    @staticmethod
    async def has_password(user: User) -> bool:
        """Check if user has a password set."""
        return bool(user.hashed_password)

    @staticmethod
    async def is_active(user: User) -> bool:
        """Check if user is active."""
        return user.is_active

    @staticmethod
    async def is_superuser(user: User) -> bool:
        """Check if user is a superuser."""
        return user.is_superuser

    @staticmethod
    async def is_email_validated(user: User) -> bool:
        """Check if user's email is validated."""
        return user.email_validated

    async def update_balance(
        self,
        db: AsyncSession,
        *,
        user_id: Any,
        balance_rub: int
    ) -> Optional[User]:
        """
        Updates user's balance.
        
        Args:
            db: Async database session
            user_id: User's UUID
            balance_rub: New balance value
            
        Returns:
            Updated User object or None if not found
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        
        if not user:
            logger.error(f"User {user_id} not found for balance update")
            return None
        
        user.balance_rub = balance_rub
        await db.commit()
        await db.refresh(user)
        logger.info(f"Updated balance for user {user_id} to {balance_rub}")
        return user


user = CRUDUser(User)
