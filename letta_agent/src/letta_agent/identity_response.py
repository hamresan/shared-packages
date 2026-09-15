from letta_client import BaseModel
from pydantic import ConfigDict


class LettaIdentityResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    identifier_key: str
    name: str
