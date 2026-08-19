from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserLogin(UserRegister):
    pass

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserActiveUpdate(BaseModel):
    is_active: bool

class SpecialtyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1000)

class SpecialtyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool | None = None

class SpecialtyResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DoctorCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=150)
    specialty_id: int
    license_number: str | None = Field(default=None, max_length=80)
    bio: str | None = Field(default=None, max_length=2000)

class DoctorUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    specialty_id: int | None = None
    license_number: str | None = Field(default=None, max_length=80)
    bio: str | None = Field(default=None, max_length=2000)
    is_active: bool | None = None

class DoctorResponse(BaseModel):
    id: int
    user_id: int
    email: EmailStr
    full_name: str
    specialty_id: int
    specialty_name: str
    license_number: str | None
    bio: str | None
    is_active: bool

class AvailabilityCreate(BaseModel):
    starts_at: datetime
    ends_at: datetime

class AvailabilityResponse(BaseModel):
    id: int
    doctor_id: int
    starts_at: datetime
    ends_at: datetime
    is_active: bool
    is_booked: bool = False

class AppointmentCreate(BaseModel):
    slot_id: int
    reason: str | None = Field(default=None, max_length=2000)

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    patient_email: EmailStr
    doctor_id: int
    doctor_name: str
    specialty_name: str
    scheduled_start: datetime
    scheduled_end: datetime
    status: str
    reason: str | None
    created_at: datetime
    cancelled_at: datetime | None

class AppointmentStatusUpdate(BaseModel):
    status: Literal["completed", "cancelled"]
