import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.core.config import settings
from app.db import base  # noqa: F401

# Configure logging
logger = logging.getLogger(__name__)

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


async def init_db(db: AsyncSession) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    logger.info("Starting database initialization...")
    try:
        # Check if superuser exists
        logger.info(f"Checking for existing superuser with email: {settings.FIRST_SUPERUSER}")
        user = await crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
        logger.info(f"Superuser check result: {'exists' if user else 'not found'}")
        
        if not user:
            logger.info("Creating new superuser...")
            # Create user auth with all required fields
            user_in = schemas.UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
                role="admin",  # Required field as per migration
                balance_rub=0,  # Required field as per migration
                email_validated=True,  # Sensible default for superuser
                is_active=True,  # Sensible default for superuser
                full_name="System Administrator",  # Optional but helpful
                company_name_id=1  # Required field
            )
            logger.info(f"Prepared user creation data: {user_in.model_dump(exclude={'password'})}")
            
            try:
                user = await crud.user.create(db, obj_in=user_in)
                logger.info(f"Successfully created superuser with ID: {user.id}")
            except Exception as e:
                logger.error(f"Failed to create superuser. Error type: {type(e).__name__}")
                logger.error(f"Error details: {str(e)}")
                raise
    except Exception as e:
        logger.error(f"Database initialization failed. Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        raise
    
    logger.info("Database initialization completed successfully")
