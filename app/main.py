from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, vacancies, resumes, analytics

app = FastAPI(
    title="HR Service",
    description="Service for managing employees, vacancies and candidates",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(vacancies.router)
app.include_router(resumes.router)
app.include_router(analytics.router)

@app.get("/")
async def root():
    return {"message": "HR Vacancy Service API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}