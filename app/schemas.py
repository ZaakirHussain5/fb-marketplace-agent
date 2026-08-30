from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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
            raise ValueError("Only US locations are supported")
        return "US"

    @field_validator("state_code")
    @classmethod
    def normalize_state(cls, value: str) -> str:
        value = value.upper().strip()
        if len(value) != 2 or not value.isalpha():
            raise ValueError("state_code must be a two-letter US state code")
        return value


class AgentFilters(BaseModel):
    category: str | None = None
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    keywords: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)
    locations: list[SearchLocationCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_prices(self):
        if self.min_price is not None and self.max_price is not None and self.min_price > self.max_price:
            raise ValueError("min_price cannot exceed max_price")
        return self


class SearchCreate(BaseModel):
    agent_id: int | None = None
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
    agent_id: int | None
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


class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    phone_number: str = Field(pattern=r"^\+[1-9]\d{7,14}$")
    instructions: str = Field(default="", max_length=8000)
    enabled: bool = True
    schedule_minutes: int = Field(default=30, ge=5, le=1440)
    notify_threshold: int = Field(default=80, ge=0, le=100)
    filters: AgentFilters


class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    phone_number: str | None = Field(default=None, pattern=r"^\+[1-9]\d{7,14}$")
    instructions: str | None = Field(default=None, max_length=8000)
    enabled: bool | None = None
    schedule_minutes: int | None = Field(default=None, ge=5, le=1440)
    notify_threshold: int | None = Field(default=None, ge=0, le=100)
    filters: AgentFilters | None = None


class AgentRead(BaseModel):
    id: int
    name: str
    phone_number: str
    instructions: str
    enabled: bool
    schedule_minutes: int
    notify_threshold: int
    filters: AgentFilters
    last_run_at: datetime | None
    next_run_at: datetime | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AgentRunRead(BaseModel):
    id: int
    agent_id: int
    trigger: str
    status: str
    collected: int
    matched: int
    notified: int
    error: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
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


class MatchRead(BaseModel):
    id: int
    search_id: int
    listing_id: int
    run_id: int | None
    score: int
    reasons: list[str]
    risks: list[str]
    should_notify: bool
    delivery_status: str
    delivery_error: str | None
    notified_at: datetime | None
    created_at: datetime
    listing: ListingRead


class SearchRunResult(BaseModel):
    collected: int
    matched: int
    notified: int
