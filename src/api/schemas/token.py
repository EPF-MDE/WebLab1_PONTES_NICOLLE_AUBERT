import logging
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)

class Token(BaseModel):
    access_token: str
    token_type: str

    def __init__(self, **data):
        logger.debug(f"Initializing Token with data: {data}")
        super().__init__(**data)

class TokenPayload(BaseModel):
    sub: Optional[int] = None

    def __init__(self, **data):
        logger.debug(f"Initializing TokenPayload with data: {data}")
        super().__init__(**data)