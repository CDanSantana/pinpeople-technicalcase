from fastapi import FastAPI, Depends, HTTPException, status
from fastauth import FastAuth
import logging
from sqlmodel import Session, create_engine, SQLModel, select
from sqlalchemy import inspect
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager
from router_factore import create_crud_router
from fastauth.models import User, Role, UserRole
from sqlalchemy.orm import sessionmaker
from  sqlalchemy.orm import declarative_base
from dynaconf import Dynaconf, Validator


settings = Dynaconf(
    envvar_prefix="APP",
    settings_files=[ '.env'],
    load_dotenv=True,
    validators=[
        Validator("DATABASE_URL", default="sqlite:///:memory:"),
        Validator("DATABASE_DRIVER", default="sqlite"),
        Validator("ENABLE_SENTIMENT_ENDPOINT", default=False),
    ]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

DATABASE_URL = settings.DATABASE_URL
#DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(DATABASE_URL,  echo=False, connect_args={"check_same_thread": False} if settings.DATABASE_DRIVER=='sqlite' else {}, poolclass=StaticPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logger = logging.getLogger("uvicorn")

auth = FastAuth(
    secret_key="a-secret-key-that-should-be-changed",
    algorithm="HS256",
    engine=engine,
    use_cookie=False,
    access_token_expires_in=30,
    refresh_token_expires_in=1,
)


def load_routes():
    from models import Area, Cargo, Funcao, Localidade, TempoEmpresa, Genero, Geracao, OrganizationalUnit, Participante, RespostaPesquisa
    for model in [Area, Cargo, Funcao, Localidade, TempoEmpresa, Genero, Geracao, OrganizationalUnit, Participante, RespostaPesquisa]:
        app.include_router(
            create_crud_router(
                model=model,
                prefix=f"/{model.get_snake_case_name()}",
                session_dep=get_session,
                allowed_filters=[field for field in model.model_fields],
                auth=auth,
            )
        )
    from analytics_router import router
    app.include_router(router=router)


def get_session():
    with Session(engine) as session:
        yield session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if not table_names:
        from models import Area, Participante
        from data_setup import load_data
        SQLModel.metadata.create_all(engine)
        logger.info('Database created')
        load_data(engine)
        auth.initialize_db(
            create_tables=True,
            init_roles=True,
            create_admin=True,
            admin_username="superadmin",
            admin_password="superadmin"
        )
        with Session(engine) as session:
            participantes = session.exec(select(Participante)).all()
            role = session.exec(select(Role).where(Role.name == "verified")).first()
            password = auth.password_manager.get_password_hash('123456')
            for participante in participantes:
                searched_user = session.exec(select(User).where(User.email == participante.email and User.username == participante.email_corporativo)).first()
                if searched_user is not None:
                    continue
                user = User(disabled=False, username=participante.email_corporativo, email=participante.email, hashed_password=password)
                session.add(user)
                session.commit()
                session.refresh(user)
                user_role = UserRole(user_id=user.id, role_id=role.id)
                session.add(user_role)
                session.commit()
    else:
        logger.info('Tables already exist')



app.include_router(
    auth.get_auth_router(get_session),
    tags=["authentication"]
)


#@app.post('/token')
#async def create_token(body: dict):
#    print(body)
#    return {'access_token': auth.create_access_token(body)}



load_routes()

@app.get("/")
async def root():
    return {"message": "Hello World"}
