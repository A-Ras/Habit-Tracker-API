from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


def _get_owned_task(db: Session, task_id: int, user_id: int):
    task = crud.get_task(db, task_id)
    if not task or task.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Task nicht gefunden")
    return task


@router.post("/", response_model=schemas.TaskResponse)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = crud.get_project(db, task.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    return crud.create_task(db=db, task=task)


from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


def _get_owned_task(db: Session, task_id: int, user_id: int):
    task = crud.get_task(db, task_id)
    if not task or task.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Task nicht gefunden")
    return task


@router.post("/", response_model=schemas.TaskResponse)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = crud.get_project(db, task.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    return crud.create_task(db=db, task=task)


@router.get("/", response_model=list[schemas.TaskResponse])
def list_tasks(
    status: Optional[schemas.TaskStatus] = None,
    priority: Optional[schemas.Priority] = None,
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_tasks(
        db=db,
        status=status,
        priority=priority,
        project_id=project_id,
        owner_id=current_user.id,  # ← HIER wird es benutzt!
        skip=skip,
        limit=limit,
    )


@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return _get_owned_task(db, task_id, current_user.id)


@router.patch("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _get_owned_task(db, task_id, current_user.id)
    db_task = crud.update_task(db, task_id=task_id, task_update=task)
    return db_task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _get_owned_task(db, task_id, current_user.id)
    crud.delete_task(db, task_id=task_id)
    return {"detail": "Task erfolgreich gelöscht", "task_id": task_id}


@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return _get_owned_task(db, task_id, current_user.id)


@router.patch("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _get_owned_task(db, task_id, current_user.id)
    db_task = crud.update_task(db, task_id=task_id, task_update=task)
    return db_task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _get_owned_task(db, task_id, current_user.id)
    crud.delete_task(db, task_id=task_id)
    return {"detail": "Task erfolgreich gelöscht", "task_id": task_id}

