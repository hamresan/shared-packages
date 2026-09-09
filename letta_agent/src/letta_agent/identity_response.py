from letta_client import BaseModel


class LettaIdentityResponse(BaseModel):
    id: str
    identifier_key: str
    name: str
