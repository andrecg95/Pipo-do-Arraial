from pydantic import BaseModel, Field, HttpUrl


class Music(BaseModel):
    uuid: str = Field(
        regex=r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )
    server_id: str
    provider: str   # TODO change to enum later
    operation: str  # TODO change to enum later
    source: HttpUrl