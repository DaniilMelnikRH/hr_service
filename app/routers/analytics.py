from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Vacancy, Resume, VacancyResume, VacancyStatus, ResumeStatus
from app.schemas import VacancyAnalytics, StatisticsResponse
from app.auth import get_current_user
from app.models import User
from typing import List

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/vacancy/{vacancy_id}/candidates", response_model=VacancyAnalytics)
async def get_vacancy_candidates(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vacancy_result = await db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = vacancy_result.scalar_one_or_none()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    total_result = await db.execute(
        select(func.count()).where(VacancyResume.vacancy_id == vacancy_id)
    )
    total_candidates = total_result.scalar()
    
    active_result = await db.execute(
        select(func.count())
        .join(VacancyResume.resume)
        .where(VacancyResume.vacancy_id == vacancy_id, Resume.status == ResumeStatus.ACTIVE)
    )
    active_candidates = active_result.scalar()
    
    return VacancyAnalytics(
        vacancy_id=vacancy.id,
        vacancy_title=vacancy.title,
        candidates_count=total_candidates,
        active_resumes_count=active_candidates
    )

@router.get("/statistics", response_model=StatisticsResponse)
async def get_general_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_vacancies_result = await db.execute(select(func.count()).select_from(Vacancy))
    total_vacancies = total_vacancies_result.scalar()
    
    open_vacancies_result = await db.execute(
        select(func.count()).where(Vacancy.status == VacancyStatus.OPEN)
    )
    open_vacancies = open_vacancies_result.scalar()
    
    closed_vacancies_result = await db.execute(
        select(func.count()).where(Vacancy.status == VacancyStatus.CLOSED)
    )
    closed_vacancies = closed_vacancies_result.scalar()
    
    total_resumes_result = await db.execute(select(func.count()).select_from(Resume))
    total_resumes = total_resumes_result.scalar()
    
    active_resumes_result = await db.execute(
        select(func.count()).where(Resume.status == ResumeStatus.ACTIVE)
    )
    active_resumes = active_resumes_result.scalar()
    
    hired_resumes_result = await db.execute(
        select(func.count()).where(Resume.status == ResumeStatus.HIRED)
    )
    hired_resumes = hired_resumes_result.scalar()
    
    return StatisticsResponse(
        total_vacancies=total_vacancies or 0,
        open_vacancies=open_vacancies or 0,
        closed_vacancies=closed_vacancies or 0,
        total_resumes=total_resumes or 0,
        active_resumes=active_resumes or 0,
        hired_resumes=hired_resumes or 0
    )