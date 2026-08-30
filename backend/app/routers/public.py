from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.appointment import Appointment
from app.models.availability import AvailabilitySlot
from app.models.doctor import DoctorProfile
from app.models.specialty import Specialty
from app.models.user import User
from app.schemas import AvailabilityResponse, DoctorResponse, SpecialtyResponse

router = APIRouter(tags=["Catalog"])
MAX_ACTIVE_APPOINTMENTS_PER_DOCTOR = 3


def doctor_response(profile, user, specialty):
    return DoctorResponse(
        id=profile.id,
        user_id=user.id,
        email=user.email,
        full_name=profile.full_name,
        specialty_id=specialty.id,
        specialty_name=specialty.name,
        license_number=profile.license_number,
        bio=profile.bio,
        is_active=user.is_active,
    )


@router.get("/specialties", response_model=list[SpecialtyResponse])
def list_specialties(db: Session = Depends(get_db)):
    return db.scalars(
        select(Specialty)
        .where(Specialty.is_active.is_(True))
        .order_by(Specialty.name)
    ).all()


@router.get("/doctors", response_model=list[DoctorResponse])
def list_doctors(
    specialty_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = (
        select(DoctorProfile, User, Specialty)
        .join(User, User.id == DoctorProfile.user_id)
        .join(Specialty, Specialty.id == DoctorProfile.specialty_id)
        .where(
            User.is_active.is_(True),
            Specialty.is_active.is_(True),
        )
        .order_by(DoctorProfile.full_name)
    )
    if specialty_id is not None:
        stmt = stmt.where(DoctorProfile.specialty_id == specialty_id)

    return [doctor_response(p, u, s) for p, u, s in db.execute(stmt).all()]


@router.get("/doctors/{doctor_id}/availability", response_model=list[AvailabilityResponse])
def get_doctor_availability(
    doctor_id: int,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
):
    doctor = db.get(DoctorProfile, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")

    active_appointments = db.scalar(
        select(func.count(Appointment.id)).where(
            Appointment.doctor_id == doctor_id,
            Appointment.status == "scheduled",
        )
    )
    remaining_slots = MAX_ACTIVE_APPOINTMENTS_PER_DOCTOR - active_appointments
    if remaining_slots <= 0:
        return []

    start = date_from or datetime.now(timezone.utc)
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)

    stmt = (
        select(AvailabilitySlot)
        .where(
            AvailabilitySlot.doctor_id == doctor_id,
            AvailabilitySlot.is_active.is_(True),
            AvailabilitySlot.starts_at >= start,
            ~exists(
                select(Appointment.id).where(
                    Appointment.slot_id == AvailabilitySlot.id
                )
            ),
        )
        .order_by(AvailabilitySlot.starts_at)
        .limit(remaining_slots)
    )

    if date_to is not None:
        end = date_to if date_to.tzinfo else date_to.replace(tzinfo=timezone.utc)
        stmt = stmt.where(AvailabilitySlot.starts_at <= end)

    return [
        AvailabilityResponse(
            id=s.id,
            doctor_id=s.doctor_id,
            starts_at=s.starts_at,
            ends_at=s.ends_at,
            is_active=s.is_active,
            is_booked=False,
        )
        for s in db.scalars(stmt).all()
    ]
