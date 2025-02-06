import logging

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession

from .user import User

logger = logging.getLogger(__name__)

@event.listens_for(User, 'after_insert')
async def create_company_view(mapper, connection, target):
    """Create a view for the company after user creation"""
    view_name = f"company_calls_{target.company_name_id}"
    
    try:
        # SQL for creating VIEW
        view_sql = text(f"""
        CREATE OR REPLACE VIEW company_calls_{target.company_name_id} AS
        SELECT *
        FROM call_analysis_results
        WHERE company_name_id = {target.company_name_id}
        """)
        
        # Execute VIEW creation
        await connection.execute(view_sql)
        logger.info(f"Successfully created view {view_name} for user {target.company_name_id}")
    except Exception as e:
        logger.error(f"Failed to create view {view_name}: {str(e)}")
        raise

@event.listens_for(User, 'after_delete')
async def drop_company_view(mapper, connection, target):
    """Drop the company view after user deletion"""
    view_name = f"company_calls_{target.company_name_id}"
    
    try:
        # SQL for dropping VIEW
        drop_sql = text(f"DROP VIEW IF EXISTS {view_name}")
        
        # Execute VIEW deletion
        await connection.execute(drop_sql)
        await connection.commit()
        logger.info(f"Successfully dropped view {view_name} for user {target.company_name_id}")
    except Exception as e:
        logger.error(f"Failed to drop view {view_name}: {str(e)}")
        raise
