from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Payment(BaseModel):
    amount: float

class AttendanceLogBase(BaseModel):
    timestamp: datetime

class AttendanceLog(AttendanceLogBase):
    id: int
    member_id: int
    addon_tag: Optional[str] = None

    class Config:
        from_attributes = True

class SubscriptionBase(BaseModel):
    package_name: List[str]
    total_price: float
    discount: float = 0
    amount_paid: float
    amount_owed: float
    total_sessions: Optional[int]
    attended_sessions: int = 0
    addons_usage: Optional[dict] = {}
    start_date: datetime
    end_date: datetime

class SubscriptionCreate(BaseModel):
    packages: List[str]
    amount_paid: float
    discount: float = 0  # Optional discount amount
    start_date: Optional[datetime] = None

class Subscription(SubscriptionBase):
    id: int
    member_id: int

    class Config:
        from_attributes = True

class MemberBase(BaseModel):
    name: str
    phone: Optional[str] = None
    gender: Optional[str] = None

class MemberCreate(MemberBase):
    subscription: SubscriptionCreate

class MemberUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None

class SubscriptionUpdate(BaseModel):
    packages: List[str]
    amount_paid: float
    discount: float = 0  # Optional discount amount

class PaymentCreate(BaseModel):
    amount: float

class FreezeRequest(BaseModel):
    duration_weeks: int  # 1 or 2 weeks options

class Member(MemberBase):
    id: int
    status: str
    frozen_at: Optional[datetime] = None
    subscriptions: List[Subscription] = []
    attendance_logs: List[AttendanceLog] = []

    class Config:
        from_attributes = True

# ─── Package Rule Schemas ────────────────────────────────────────────────────

class PackageRuleBase(BaseModel):
    name: str
    price: float
    duration_days: int
    sessions: Optional[int] = None  # null = unlimited
    is_addon: bool = False

class PackageRuleCreate(PackageRuleBase):
    pass

class PackageRuleUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    duration_days: Optional[int] = None
    sessions: Optional[int] = None
    is_addon: Optional[bool] = None

class PackageRule(PackageRuleBase):
    id: int

    class Config:
        from_attributes = True

# ─── Receptionist Schemas ────────────────────────────────────────────────────

class ReceptionistBase(BaseModel):
    name: str

class ReceptionistCreate(ReceptionistBase):
    pass

class ReceptionistUpdate(BaseModel):
    name: Optional[str] = None

class Receptionist(ReceptionistBase):
    id: int

    class Config:
        from_attributes = True

# ─── Finance Schemas ──────────────────────────────────────────────────────────

class StaffBase(BaseModel):
    name: str
    phone: Optional[str] = None
    role: str
    base_salary: float
    pay_day: int = 1

class StaffCreate(StaffBase):
    pass

class StaffUpdate(BaseModel):
    pending_bonus: float
    pending_deduction: float

class StaffResponse(StaffBase):
    id: int
    pending_bonus: float
    pending_deduction: float
    last_paid_date: datetime
    created_at: datetime
    class Config:
        from_attributes = True

class ExpenseCreate(BaseModel):
    category: str
    amount: float
    description: Optional[str] = None
    date: Optional[datetime] = None

class ExpenseResponse(BaseModel):
    id: int
    category: str
    amount: float
    description: Optional[str] = None
    date: datetime
    class Config:
        from_attributes = True
