from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import datetime


# ── Module ────────────────────────────────────────────────────────────────────
class ModuleBase(BaseModel):
    title: str = Field(description="The name of this module")
    description: str = Field(description="Short description of what the user will learn")
    order_index: int = Field(description="The sequential ordering of this module")
    search_query: str = Field(description="A concise, highly specific YouTube search query for this exact module topic. MUST include the skill name and the specific sub-topic. Example for a Python setup module: 'python install setup pip venv IDE beginner'. Never use generic phrases like 'how to' or 'best practices' alone.")


class ModuleResponse(BaseModel):
    id: int
    title: str
    description: str
    video_id: Optional[str]
    video_duration: Optional[int] = 0
    is_completed: bool
    is_skipped: bool
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# ── Course ────────────────────────────────────────────────────────────────────
class CourseCreate(BaseModel):
    skill_name: str
    start_level: int = Field(ge=0, le=10, description="User's starting skill level")
    time_commitment: str
    modules: List[ModuleBase] = Field(description="List of ordered modules to learn the skill")


class CourseResponse(BaseModel):
    id: int
    skill_name: str
    current_level: int
    time_commitment: str
    is_public: bool = False

    class Config:
        from_attributes = True


class CoursePublicResponse(BaseModel):
    """Used in the Discover / Marketplace tab."""
    id: int
    skill_name: str
    current_level: int
    time_commitment: str
    owner_username: Optional[str] = None
    module_count: Optional[int] = 0

    class Config:
        from_attributes = True


class PaginatedCoursesResponse(BaseModel):
    """Envelope for the paginated/filterable /courses/public marketplace listing."""
    items: List[CoursePublicResponse]
    total: int
    limit: int
    offset: int


# ── Quiz ──────────────────────────────────────────────────────────────────────
class QuizQuestion(BaseModel):
    question: str
    options: List[str] = Field(min_length=4, max_length=4, description="Four multiple-choice options")
    correct_answer_index: int = Field(ge=0, le=3)
    explanation: str = Field(description="Brief explanation of why the answer is correct")


class Quiz(BaseModel):
    module_id: int
    questions: List[QuizQuestion] = Field(min_length=1, max_length=5, description="Up to 5 questions")


# ── Flashcards ────────────────────────────────────────────────────────────────
class Flashcard(BaseModel):
    front: str = Field(description="The question or term shown on the front of the card")
    back: str = Field(description="The answer or definition shown on the back of the card")


class FlashcardSet(BaseModel):
    module_id: int
    cards: List[Flashcard] = Field(min_length=1, max_length=5, description="3 to 5 flashcards")


# ── Auth ──────────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ── Notes ─────────────────────────────────────────────────────────────────────
class NoteUpdate(BaseModel):
    notes: str


# ── Module completion ─────────────────────────────────────────────────────────
class ModuleCompleteRequest(BaseModel):
    watch_time: int = Field(ge=0, description="Seconds of video the user actively watched")

# ── Live Tutor Chat ─────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

# ── Job Ready Calculator ──────────────────────────────────────────────────
class JobReadyRequest(BaseModel):
    job_title: str
    company: str

class JobReadyResponse(BaseModel):
    readiness_percentage: int
    missing_skills: List[str]
    suggested_modules: List[str]
    roadmap: List[str]
    estimated_time: str

# ── Skill Graph ───────────────────────────────────────────────────────────
class SkillNode(BaseModel):
    id: str
    name: str
    val: int
    completed: bool

class SkillLink(BaseModel):
    source: str
    target: str

class SkillGraphResponse(BaseModel):
    nodes: List[SkillNode]
    links: List[SkillLink]

# ── Progress Analytics ────────────────────────────────────────────────────
class ProgressResponse(BaseModel):
    courses_count: int
    total_modules: int
    modules_completed: int
    completion_rate: float
    last_completed_at: Optional[datetime.datetime] = None

