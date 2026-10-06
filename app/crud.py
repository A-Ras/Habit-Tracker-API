from typing import Optional
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session, joinedload
from app import models, schemas
import bcrypt


def get_password_hash(password: str) -> str:
    """Hasht ein Passwort mit bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Prüft ein Passwort gegen einen Hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# ═══════════════════════════════════════════════════════════════
# USER
# ═══════════════════════════════════════════════════════════════

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ═══════════════════════════════════════════════════════════════
# PROJECT
# ═══════════════════════════════════════════════════════════════

def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_project_with_tasks(db: Session, project_id: int):
    return (
        db.query(models.Project)
        .options(joinedload(models.Project.tasks))  # Lädt die zugehörigen Aufgaben mit
        .filter(models.Project.id == project_id)
        .first()
    )

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate, owner_id: int):
    # Sternchen-Operator entpackt die Felder des Pydantic-Modells in ein Dictionary, das dann an das SQLAlchemy-Modell übergeben wird.
    db_project = models.Project(**project.model_dump(), owner_id=owner_id) 
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# ═══════════════════════════════════════════════════════════════
# TASK
# ═══════════════════════════════════════════════════════════════

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(
    db: Session,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    project_id: Optional[int] = None,
    owner_id: Optional[int] = None,  # ← NEU!
    skip: int = 0,
    limit: int = 100,
):
    """Filtert Tasks nach Status, Priorität, Projekt UND Owner."""
    from sqlalchemy.orm import joinedload
    
    # Wir joinen Project, um nach owner_id filtern zu können
    query = db.query(models.Task).join(models.Project)
    
    if owner_id:
        query = query.filter(models.Project.owner_id == owner_id)
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    if project_id:
        query = query.filter(models.Task.project_id == project_id)
    
    return query.offset(skip).limit(limit).all()

def create_task(db: Session, task: schemas.TaskCreate):
    # Sternchen-Operator entpackt die Felder des Pydantic-Modells in ein Dictionary, das dann an das SQLAlchemy-Modell übergeben wird.
    db_task = models.Task(**task.model_dump()) 
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return None
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    # Sternchen-Operator entpackt die Felder des Pydantic-Modells in ein Dictionary, das dann an das SQLAlchemy-Modell übergeben wird.
    db_task.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task

# ═══════════════════════════════════════════════════════════════
# HABIT
# ═══════════════════════════════════════════════════════════════

def get_habit(db: Session, habit_id: int):
    return db.query(models.Habit).filter(models.Habit.id == habit_id).first()

def get_habits(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Habit).offset(skip).limit(limit).all()

def create_habit(db: Session, habit: schemas.HabitCreate):
    db_habit = models.Habit(**habit.model_dump()) # Es wird ein Habit-Objekt erstellt, das die Felder aus dem Pydantic-Modell übernimmt.
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

# ═══════════════════════════════════════════════════════════════
# HABIT CHECK-IN
# ═══════════════════════════════════════════════════════════════

def get_checkin(db: Session, checkin_id: int):
    return db.query(models.HabitCheckIn).filter(models.HabitCheckIn.id == checkin_id).first()

def get_checkins_by_habit(db: Session, habit_id: int):
    return (
        db.query(models.HabitCheckIn)
        .filter(models.HabitCheckIn.habit_id == habit_id)
        .order_by(models.HabitCheckIn.check_date.desc())
        .all()
    )

def create_checkin(db: Session, habit_id: int, checkin: schemas.HabitCheckInCreate):
    db_checkin = models.HabitCheckIn(
        habit_id=habit_id,
        check_date=checkin.check_date,
        completed=checkin.completed,
    )
    db.add(db_checkin)
    db.commit()
    db.refresh(db_checkin)
    return db_checkin

def delete_checkin(db: Session, checkin_id: int):
    db_checkin = db.query(models.HabitCheckIn).filter(models.HabitCheckIn.id == checkin_id).first()
    if db_checkin:
        db.delete(db_checkin)
        db.commit()
    return db_checkin


# ═══════════════════════════════════════════════════════════════
# STREAK BERECHNUNG
# ═══════════════════════════════════════════════════════════════

def _calc_daily_streaks(dates: list[date]) -> tuple[int, int]:
    """Berechnet current und best streak für tägliche Habits."""
    if not dates:
        return 0, 0

    today = date.today()
    sorted_dates = sorted(set(dates))  # Aufsteigend, Duplikate entfernen

    # Current streak: rückwärts von heute zählen
    current = 0
    if (today - sorted_dates[-1]).days <= 1:  # Heute oder gestern
        current = 1
        for i in range(len(sorted_dates) - 2, -1, -1): # rückwärts durch die Liste
            if (sorted_dates[i + 1] - sorted_dates[i]).days == 1:
                current += 1
            else:
                break

    # Best streak: längste Sequenz
    best = 1
    temp = 1
    for i in range(1, len(sorted_dates)):
        diff = (sorted_dates[i] - sorted_dates[i - 1]).days
        if diff == 1:
            temp += 1
            best = max(best, temp)
        elif diff > 1:
            temp = 1

    return current, best


def _calc_weekly_streaks(dates: list[date]) -> tuple[int, int]:
    """Berechnet current und best streak für wöchentliche Habits."""
    if not dates:
        return 0, 0

    today = date.today()
    # ISO-Kalenderwoche: (year, week, weekday)
    weeks = sorted({d.isocalendar()[:2] for d in dates})  # (year, week) Tupel

    current_week = today.isocalendar()[:2]

    # Current streak
    current = 0
    if weeks[-1] == current_week or _prev_week(weeks[-1]) == current_week:
        current = 1
        for i in range(len(weeks) - 2, -1, -1):
            if _prev_week(weeks[i + 1]) == weeks[i]:
                current += 1
            else:
                break

    # Best streak
    best = 1
    temp = 1
    for i in range(1, len(weeks)):
        if _prev_week(weeks[i]) == weeks[i - 1]:
            temp += 1
            best = max(best, temp)
        else:
            temp = 1

    return current, best


def _prev_week(year_week: tuple) -> tuple:
    """Hilfsfunktion: Gibt die vorherige ISO-Woche zurück."""
    from datetime import timedelta
    y, w = year_week
    d = date.fromisocalendar(y, w, 1) - timedelta(weeks=1)
    return d.isocalendar()[:2]


def calculate_streaks(db: Session, habit_id: int, frequency: str) -> tuple[int, int]:
    """Berechnet current_streak und best_streak für ein Habit."""
    checkins = (
        db.query(models.HabitCheckIn)
        .filter(
            models.HabitCheckIn.habit_id == habit_id,
            models.HabitCheckIn.completed == True,
        )
        .all()
    )
    dates = [c.check_date for c in checkins]

    if frequency == "daily":
        return _calc_daily_streaks(dates)
    else:
        return _calc_weekly_streaks(dates)


def update_habit_streaks(db: Session, habit: models.Habit):
    """Aktualisiert die Streak-Felder eines Habits in der DB."""
    current, best = calculate_streaks(db, habit.id, habit.frequency)
    habit.current_streak = current
    habit.best_streak = max(habit.best_streak, best)
    db.commit()
    db.refresh(habit)
    return habit    