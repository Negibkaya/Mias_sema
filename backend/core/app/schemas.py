from pydantic import BaseModel, Field
from typing import Optional


class Skill(BaseModel):
    name: str
    level: int = Field(ge=0, le=10)



class Role(BaseModel):
    name: str
    count: int = Field(ge=1, le=100, default=1)
    skills: list[Skill] = []


class UserPublic(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str] = None
    name: Optional[str] = None
    skills: Optional[list[Skill]] = None
    bio: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    skills: Optional[list[Skill]] = None
    bio: Optional[str] = None


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    roles: Optional[list[Role]] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    roles: Optional[list[Role]] = None


class ProjectPublic(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    roles: Optional[list[Role]] = None
    owner_id: int

    class Config:
        from_attributes = True


class ProjectMemberPublic(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str] = None
    name: Optional[str] = None
    skills: Optional[list[Skill]] = None
    bio: Optional[str] = None
    role_name: Optional[str] = None

    class Config:
        from_attributes = True


class LoginCompleteIn(BaseModel):
    code: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MatchRequestIn(BaseModel):
    project_id: int
    role_name: Optional[str] = None
    top_n: int = Field(default=3, ge=1, le=20)


class MatchResultItem(BaseModel):
    id: int
    score: int
    reason: str


class RoleMatchResult(BaseModel):
    role_name: str
    needed: int  # сколько нужно
    filled: int  # сколько уже есть
    candidates: list[MatchResultItem]