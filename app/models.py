from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class VacancyStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"

class ResumeStatus(str, enum.Enum):
    ACTIVE = "active"
    HIRED = "hired"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    vacancies = relationship("Vacancy", back_populates="category")

class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    vacancies = relationship("Vacancy", back_populates="position")

class Vacancy(Base):
    __tablename__ = "vacancies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    location = Column(String(200), nullable=True)
    status = Column(SQLEnum(VacancyStatus), default=VacancyStatus.OPEN)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)
    
    category = relationship("Category", back_populates="vacancies")
    position = relationship("Position", back_populates="vacancies")
    resumes = relationship("VacancyResume", back_populates="vacancy", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String(100), nullable=False)
    candidate_email = Column(String(100), nullable=False)
    candidate_phone = Column(String(20), nullable=True)
    skills = Column(Text, nullable=True)  # Хранение навыков в текстовом виде (можно улучшить отдельной таблицей)
    experience_years = Column(Integer, default=0)
    status = Column(SQLEnum(ResumeStatus), default=ResumeStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    vacancies = relationship("VacancyResume", back_populates="resume", cascade="all, delete-orphan")

class VacancyResume(Base):
    """Связующая таблица для откликов на вакансии"""
    __tablename__ = "vacancy_resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    cover_letter = Column(Text, nullable=True)
    
    vacancy = relationship("Vacancy", back_populates="resumes")
    resume = relationship("Resume", back_populates="vacancies")