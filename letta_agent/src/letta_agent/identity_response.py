from pydantic import BaseModel, ConfigDict


class LettaIdentityResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    identifier_key: str
    name: str
