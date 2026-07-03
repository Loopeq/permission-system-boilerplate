from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: str = Field(max_length=255)
    password: str = Field(min_length=6)
    password_again: str = Field(min_length=6)

class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=6)

class UserRead(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PermissionCreate(BaseModel):
    code: str = Field(min_length=3, max_length=255)
    description: str | None = Field(default=None, max_length=500)

class PermissionRead(BaseModel):
    id: int
    code: str
    description: str | None

    model_config = {"from_attributes": True}

class GrantPermissionRequest(BaseModel):
    permission_id: int

class UserPermissionRead(BaseModel):
    permission_id: int
    code: str
    description: str | None
