from pydantic import BaseModel, ConfigDict, Field, field_validator


class SearchLocationCreate(BaseModel):
    country_code: str = "US"
    state_code: str
    city: str | None = None
    postal_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    radius_miles: float | None = Field(default=None, gt=0, le=500)

    @field_validator("country_code")
    @classmethod
    def us_only(cls, value: str) -> str:
        if value.upper() != "US":
            raise ValueError("Only US locations are supported in the MVP")
        return "US"

    @field_validator("state_code")
    @classmethod
    def normalize_state(cls, value: str) -> str:
        value = value.upper().strip()
        if len(value) != 2:
            raise ValueError("state_code must be a two-letter US state code")
        return value


class SearchCreate(BaseModel):
    name: str
    category: str | None = None
    keywords: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    notify_threshold: int = Field(default=80, ge=0, le=100)
    locations: list[SearchLocationCreate] = Field(min_length=1)


class SearchLocationRead(SearchLocationCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SearchRead(BaseModel):
    id: int
    name: str
    category: str | None
    keywords: list[str]
    exclude_keywords: list[str]
    min_price: float | None
    max_price: float | None
    enabled: bool
    notify_threshold: int
    locations: list[SearchLocationRead]
    model_config = ConfigDict(from_attributes=True)


class ListingRead(BaseModel):
    id: int
    external_id: str
    title: str
    description: str | None
    category: str | None
    price: float | None
    currency: str
    url: str
    state_code: str | None
    city: str | None
    postal_code: str | None
    model_config = ConfigDict(from_attributes=True)


class SearchRunResult(BaseModel):
    collected: int
    matched: int
    notified: int
