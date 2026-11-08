from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone
from time_utils import get_current_time

Base = declarative_base()

class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    status = Column(String, default="Active") # Active, Owed Money, Expired, Inactive, Frozen
    frozen_at = Column(DateTime, nullable=True)
    freeze_end_date = Column(DateTime, nullable=True)
    expired_at = Column(DateTime, nullable=True)

    subscriptions = relationship("Subscription", back_populates="member", cascade="all, delete-orphan")
    attendance_logs = relationship("AttendanceLog", back_populates="member", cascade="all, delete-orphan")

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    package_name = Column(JSON) # Array of strings
    total_price = Column(Float)
    discount = Column(Float, default=0)  # Discount amount applied
    amount_paid = Column(Float)
    amount_owed = Column(Float)
    total_sessions = Column(Integer, nullable=True)
    attended_sessions = Column(Integer, default=0)
    addons_usage = Column(JSON, default=list)
    start_date = Column(DateTime)
    end_date = Column(DateTime, index=True)

    member = relationship("Member", back_populates="subscriptions")

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    timestamp = Column(DateTime, default=get_current_time)
    addon_tag = Column(String, nullable=True)

    member = relationship("Member", back_populates="attendance_logs")

class PackageRule(Base):
    __tablename__ = "package_rules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    price = Column(Float)
    duration_days = Column(Integer)
    sessions = Column(Integer, nullable=True)  # null = unlimited
    is_addon = Column(Boolean, default=False)

class Receptionist(Base):
    __tablename__ = "receptionists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class AppConfig(Base):
    __tablename__ = "app_config"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)

class Staff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, nullable=True)
    role = Column(String)
    base_salary = Column(Float)
    pay_day = Column(Integer, default=1)
    pending_bonus = Column(Float, default=0)
    pending_deduction = Column(Float, default=0)
    last_paid_date = Column(DateTime, default=get_current_time)
    created_at = Column(DateTime, default=get_current_time)

    payments = relationship("StaffPayment", back_populates="staff", cascade="all, delete-orphan")

class StaffPayment(Base):
    __tablename__ = "staff_payments"
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"))
    amount = Column(Float)
    bonus = Column(Float, default=0)
    deduction = Column(Float, default=0)
    payment_date = Column(DateTime, default=get_current_time)
    
    staff = relationship("Staff", back_populates="payments")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String) # "Maintenance" or "Bill"
    amount = Column(Float)
    description = Column(String, nullable=True)
    date = Column(DateTime, default=get_current_time)

class SingleSession(Base):
    __tablename__ = "single_sessions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    amount = Column(Float)
    timestamp = Column(DateTime, default=get_current_time)
