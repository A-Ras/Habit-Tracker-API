from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)

@router.post("/", response_model=schemas.ProjectResponse)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Erstellt ein Projekt für den eingeloggten User."""
    return crud.create_project(db=db, project=project, owner_id=current_user.id)

@router.get("/", response_model=list[schemas.ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Listet nur die Projekte des eingeloggten Users."""
    return current_user.projects  # Nutzt die SQLAlchemy-Beziehung!

@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    return db_project

@router.get("/{project_id}/full", response_model=schemas.ProjectWithTasks)
def get_project_with_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_project = crud.get_project_with_tasks(db, project_id=project_id)
    if db_project is None or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    return db_project