from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ═══════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HabitFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


# ═══════════════════════════════════════════════════════════════
# USER
# ═══════════════════════════════════════════════════════════════

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# PROJECT
# ═══════════════════════════════════════════════════════════════

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")  # Hex-Farbe z. B. #FF5733


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# TASK
# ═══════════════════════════════════════════════════════════════

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[date] = None
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM


class TaskCreate(TaskBase):
    project_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[date] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None


class TaskResponse(TaskBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
  
    # Wandelt SQLAlchemy-Objekte automatisch um (später wichtig!)
    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# HABIT
# ═══════════════════════════════════════════════════════════════

class HabitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    frequency: HabitFrequency = HabitFrequency.DAILY


class HabitCreate(HabitBase):
    project_id: int


class HabitUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    frequency: Optional[HabitFrequency] = None


class HabitResponse(HabitBase):
    id: int
    project_id: int
    created_at: datetime
    current_streak: int = 0
    best_streak: int = 0

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# HABIT CHECK-IN
# ═══════════════════════════════════════════════════════════════

class HabitCheckInBase(BaseModel):
    check_date: date
    completed: bool = True


class HabitCheckInCreate(HabitCheckInBase):
    pass


class HabitCheckInResponse(HabitCheckInBase):
    id: int
    habit_id: int

    model_config = ConfigDict(from_attributes=True)

# ═══════════════════════════════════════════════════════════════
# NESTED RESPONSES (mit Beziehungen zwischen den Modellen)
# ═══════════════════════════════════════════════════════════════    

class ProjectWithTasks(ProjectResponse):
    tasks: list[TaskResponse] = []

    model_config = ConfigDict(from_attributes=True)
