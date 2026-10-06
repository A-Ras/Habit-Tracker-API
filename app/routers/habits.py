from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app import schemas, crud, models
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(
    prefix="/habits",
    tags=["habits"],
)


def _get_owned_habit(db: Session, habit_id: int, user_id: int):
    """Holt ein Habit und prüft, ob es dem User gehört."""
    habit = crud.get_habit(db, habit_id)
    if not habit or habit.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Habit nicht gefunden")
    return habit


@router.post("/", response_model=schemas.HabitResponse)
def create_habit(
    habit: schemas.HabitCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Prüfen, ob das Projekt dem User gehört
    project = crud.get_project(db, habit.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    return crud.create_habit(db=db, habit=habit)


@router.get("/", response_model=list[schemas.HabitResponse])
def list_habits(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Listet alle Habits des eingeloggten Users (optimiert mit JOIN)."""
    habits = (
        db.query(models.Habit)
        .join(models.Project)
        .filter(models.Project.owner_id == current_user.id)
        .options(joinedload(models.Habit.project))
        .all()
    )
    return habits


@router.get("/{habit_id}", response_model=schemas.HabitResponse)
def get_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    habit = _get_owned_habit(db, habit_id, current_user.id)
    # Streaks aktualisieren vor der Rückgabe
    crud.update_habit_streaks(db, habit)
    return habit


# ═══════════════════════════════════════════════════════════════
# CHECK-IN ENDPUNKTE
# ═══════════════════════════════════════════════════════════════

@router.post("/{habit_id}/checkins", response_model=schemas.HabitCheckInResponse)
def create_checkin(
    habit_id: int,
    checkin: schemas.HabitCheckInCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Check-In für ein Habit erstellen (z. B. 'Heute erledigt')."""
    habit = _get_owned_habit(db, habit_id, current_user.id)
    new_checkin = crud.create_checkin(db, habit_id=habit_id, checkin=checkin)
    # Streaks neu berechnen
    crud.update_habit_streaks(db, habit)
    return new_checkin


@router.get("/{habit_id}/checkins", response_model=list[schemas.HabitCheckInResponse])
def list_checkins(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Alle Check-Ins eines Habits anzeigen."""
    _get_owned_habit(db, habit_id, current_user.id)
    return crud.get_checkins_by_habit(db, habit_id=habit_id)


@router.delete("/{habit_id}/checkins/{checkin_id}")
def delete_checkin(
    habit_id: int,
    checkin_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Löscht einen Check-In."""
    habit = _get_owned_habit(db, habit_id, current_user.id)
    checkin = crud.get_checkin(db, checkin_id)
    if not checkin or checkin.habit_id != habit_id:
        raise HTTPException(status_code=404, detail="Check-In nicht gefunden")
    crud.delete_checkin(db, checkin_id)
    crud.update_habit_streaks(db, habit)
    return {"detail": "Check-In gelöscht", "checkin_id": checkin_id}

