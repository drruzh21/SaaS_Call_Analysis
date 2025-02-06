from datetime import datetime

import pytz
from neomodel import (
    BooleanProperty,
    DateTimeProperty,
    StructuredRel,
)


class ResourceRelationship(StructuredRel):
    created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    isActive = BooleanProperty(default=True)
