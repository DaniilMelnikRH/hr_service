from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum

class VacancyStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"

class ResumeStatus(str, Enum):
    ACTIVE = "active"
    HIRED = "hired"
    REJECTED = "rejected"

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class PositionBase(BaseModel):
    name: str = Field(..., max_length=100)

class PositionCreate(PositionBase):
    pass

class PositionResponse(PositionBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class VacancyBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: Optional[str] = None
    category_id: int
    position_id: int

class VacancyCreate(VacancyBase):
    pass

class VacancyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: Optional[str] = None
    status: Optional[VacancyStatus] = None
    category_id: Optional[int] = None
    position_id: Optional[int] = None

class VacancyResponse(VacancyBase):
    id: int
    status: VacancyStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: CategoryResponse
    position: PositionResponse
    resumes_count: Optional[int] = 0
    
    model_config = ConfigDict(from_attributes=True)

class ResumeBase(BaseModel):
    candidate_name: str = Field(..., max_length=100)
    candidate_email: EmailStr
    candidate_phone: Optional[str] = None
    skills: Optional[str] = None
    experience_years: int = Field(0, ge=0, le=50)

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(BaseModel):
    candidate_name: Optional[str] = None
    candidate_email: Optional[EmailStr] = None
    candidate_phone: Optional[str] = None
    skills: Optional[str] = None
    experience_years: Optional[int] = None
    status: Optional[ResumeStatus] = None

class ResumeResponse(ResumeBase):
    id: int
    status: ResumeStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ApplyToVacancy(BaseModel):
    resume_id: int
    cover_letter: Optional[str] = None

class VacancyAnalytics(BaseModel):
    vacancy_id: int
    vacancy_title: str
    candidates_count: int
    active_resumes_count: int

class StatisticsResponse(BaseModel):
    total_vacancies: int
    open_vacancies: int
    closed_vacancies: int
    total_resumes: int
    active_resumes: int
    hired_resumes: int