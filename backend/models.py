from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, false
from sqlalchemy.orm import relationship, validates
import datetime
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    google_sub = Column(String, unique=True, index=True, nullable=True)  # Google account subject id
    hashed_password = Column(String, nullable=True)  # legacy/unused — retained to avoid a destructive migration
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    courses = relationship("Course", back_populates="owner")
    quiz_attempts = relationship("QuizAttempt", back_populates="user")


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill_name = Column(String, index=True)
    current_level = Column(Integer)
    time_commitment = Column(String)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    project_prompt = Column(Text, nullable=True, default=None)
    required_resources = Column(Text, nullable=True, default=None)

    owner = relationship("User", back_populates="courses")
    modules = relationship("Module", back_populates="course", order_by="Module.order_index")

    @validates('required_resources')
    def validate_required_resources(self, key, value):
        if value is not None and not isinstance(value, list):
            raise ValueError("required_resources must be None or a list")
        return value


class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    description = Column(String)
    order_index = Column(Integer)
    video_id = Column(String, nullable=True)
    search_query = Column(String)
    is_completed = Column(Boolean, default=False)
    is_skipped = Column(Boolean, default=False)
    video_duration = Column(Integer, default=0)
    has_transcript = Column(Boolean, nullable=False, default=False, server_default=false())
    notes = Column(String(2000), nullable=True, default=None)
    completed_at = Column(DateTime, nullable=True, default=None)

    @validates('notes')
    def validate_notes(self, key, value):
        if value is not None and len(value) > 2000:
            raise ValueError("notes must not exceed 2000 characters")
        return value

    course = relationship("Course", back_populates="modules")
    quiz_attempts = relationship("QuizAttempt", back_populates="module")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Integer)
    passed = Column(Boolean)
    attempted_at = Column(DateTime, default=datetime.datetime.utcnow)

    module = relationship("Module", back_populates="quiz_attempts")
    user = relationship("User", back_populates="quiz_attempts")
