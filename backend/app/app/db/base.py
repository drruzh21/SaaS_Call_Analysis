# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.api_key import APIKey  # noqa
from app.models.call_analysis import CallAnalysisResult, CallObjection, Objection  # noqa
from app.models.token import Token  # noqa
from app.models.user import User  # noqa
