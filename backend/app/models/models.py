import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="student", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="user", cascade="all, delete-orphan")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    compile_status = Column(String(50), nullable=False)  # "clean", "error", "timeout", "failed"
    duration_ms = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="submissions")
    errors = relationship("ErrorRecord", back_populates="submission", cascade="all, delete-orphan")


class ErrorRecord(Base):
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    line = Column(Integer, nullable=True)
    column = Column(Integer, nullable=True)
    severity = Column(String(50), nullable=False)  # "error", "warning", "note", "fatal error"
    raw_message = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)   # filled in Module 2
    confidence = Column(Float, nullable=True)       # filled in Module 2
    is_primary = Column(Boolean, default=False, nullable=False)
    abstained = Column(Boolean, default=False, nullable=False)
    model_version = Column(String(50), nullable=True)

    submission = relationship("Submission", back_populates="errors")
    feedback = relationship("Feedback", back_populates="error_record", cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    error_id = Column(Integer, ForeignKey("errors.id", ondelete="CASCADE"), nullable=False, index=True)
    helpful = Column(Boolean, nullable=False)
    corrected_category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    error_record = relationship("ErrorRecord", back_populates="feedback")


class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    round_id = Column(Integer, ForeignKey("retraining_rounds.id", ondelete="SET NULL"), nullable=True)
    decision = Column(String(50), nullable=False)  # "granted", "denied", "pending"
    decided_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="consents")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    version = Column(String(50), primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    data_summary = Column(Text, nullable=True)
    metrics = Column(Text, nullable=True)  # JSON formatted metrics string
    checksum = Column(String(128), nullable=False)
    active = Column(Boolean, default=False, nullable=False, index=True)


class RetrainingRound(Base):
    __tablename__ = "retraining_rounds"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    status = Column(String(50), nullable=False)  # "planned", "running", "completed", "rejected"
    resulting_model_version = Column(String(50), ForeignKey("model_versions.version"), nullable=True)
