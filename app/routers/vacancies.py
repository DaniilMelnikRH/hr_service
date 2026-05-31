from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from app.database import get_db
from app.models import Vacancy, Category, Position, VacancyResume, Resume
from app.schemas import VacancyCreate, VacancyUpdate, VacancyResponse
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/vacancies", tags=["Vacancies"])

@router.get("/", response_model=List[VacancyResponse])
async def get_vacancies(
    status: Optional[str] = Query(None, regex="^(open|closed)$"),
    position_id: Optional[int] = None,
    category_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Vacancy)
    
    if status:
        query = query.where(Vacancy.status == status)
    if position_id:
        query = query.where(Vacancy.position_id == position_id)
    if category_id:
        query = query.where(Vacancy.category_id == category_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    vacancies = result.scalars().all()
    
    response_vacancies = []
    for vacancy in vacancies:
        resumes_count_result = await db.execute(
            select(func.count()).where(VacancyResume.vacancy_id == vacancy.id)
        )
        resumes_count = resumes_count_result.scalar()
        
        await db.refresh(vacancy, attribute_names=["category", "position"])
        
        vacancy_dict = VacancyResponse.model_validate(vacancy)
        vacancy_dict.resumes_count = resumes_count
        response_vacancies.append(vacancy_dict)
    
    return response_vacancies

@router.get("/{vacancy_id}", response_model=VacancyResponse)
async def get_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = result.scalar_one_or_none()
    if not vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    
    await db.refresh(vacancy, attribute_names=["category", "position"])
    
    resumes_count_result = await db.execute(
        select(func.count()).where(VacancyResume.vacancy_id == vacancy.id)
    )
    resumes_count = resumes_count_result.scalar()
    
    response = VacancyResponse.model_validate(vacancy)
    response.resumes_count = resumes_count
    return response

@router.post("/", response_model=VacancyResponse, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    vacancy_data: VacancyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category_result = await db.execute(select(Category).where(Category.id == vacancy_data.category_id))
    if not category_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")
    
    position_result = await db.execute(select(Position).where(Position.id == vacancy_data.position_id))
    if not position_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Position not found")
    
    new_vacancy = Vacancy(**vacancy_data.model_dump())
    db.add(new_vacancy)
    await db.commit()
    await db.refresh(new_vacancy)
    await db.refresh(new_vacancy, attribute_names=["category", "position"])
    
    return new_vacancy

@router.put("/{vacancy_id}", response_model=VacancyResponse)
async def update_vacancy(
    vacancy_id: int,
    vacancy_data: VacancyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = result.scalar_one_or_none()
    if not vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    
    update_data = vacancy_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vacancy, key, value)
    
    await db.commit()
    await db.refresh(vacancy)
    await db.refresh(vacancy, attribute_names=["category", "position"])
    
    return vacancy

@router.delete("/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = result.scalar_one_or_none()
    if not vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    
    await db.delete(vacancy)
    await db.commit()

@router.post("/{vacancy_id}/close")
async def close_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = result.scalar_one_or_none()
    if not vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    
    vacancy.status = "closed"
    await db.commit()
    return {"message": "Vacancy closed successfully"}

@router.post("/{vacancy_id}/apply")
async def apply_to_vacancy(
    vacancy_id: int,
    resume_id: int,
    cover_letter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vacancy_result = await db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    if not vacancy_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    
    resume_result = await db.execute(select(Resume).where(Resume.id == resume_id))
    if not resume_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    
    existing_result = await db.execute(
        select(VacancyResume).where(
            VacancyResume.vacancy_id == vacancy_id,
            VacancyResume.resume_id == resume_id
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already applied to this vacancy")
    
    application = VacancyResume(
        vacancy_id=vacancy_id,
        resume_id=resume_id,
        cover_letter=cover_letter
    )
    db.add(application)
    await db.commit()
    
    return {"message": "Successfully applied to vacancy"}