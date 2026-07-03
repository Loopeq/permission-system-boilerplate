from fastapi import FastAPI

from src.data.database import SessionLocal, engine
from src.data.seeder import seed_boilerplate_data
from src.models import Base

from src.api.auth import router as auth_router
from src.api.user import router as users_router
from src.api.documents import router as documents_router
from src.api.admin import router as admin_router


app = FastAPI()

# Роуты
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_boilerplate_data(db)
    finally:
        db.close()


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(documents_router)
app.include_router(admin_router)

