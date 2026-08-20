from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_roles
from app.models.appointment import Appointment
from app.models.availability import AvailabilitySlot
from app.models.doctor import DoctorProfile
from app.models.specialty import Specialty
from app.models.user import User
from app.schemas import AppointmentCreate, AppointmentResponse

router = APIRouter(prefix="/appointments", tags=["Patient appointments"])

def _appointment_response(db: Session, appointment: Appointment) -> AppointmentResponse:
    patient = db.get(User, appointment.patient_id)
    doctor = db.get(DoctorProfile, appointment.doctor_id)
    specialty = db.get(Specialty, doctor.specialty_id) if doctor else None
    if patient is None or doctor is None or specialty is None:
        raise HTTPException(status_code=500, detail="Appointment references invalid data")
    return AppointmentResponse(id=appointment.id, patient_id=appointment.patient_id, patient_email=patient.email, doctor_id=doctor.id, doctor_name=doctor.full_name, specialty_name=specialty.name, scheduled_start=appointment.scheduled_start, scheduled_end=appointment.scheduled_end, status=appointment.status, reason=appointment.reason, created_at=appointment.created_at, cancelled_at=appointment.cancelled_at)

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(data: AppointmentCreate, current_user: User = Depends(require_roles("patient")), db: Session = Depends(get_db)):
    slot = db.scalar(select(AvailabilitySlot).where(AvailabilitySlot.id == data.slot_id).with_for_update())
    if slot is None or not slot.is_active:
        raise HTTPException(status_code=404, detail="Availability slot not found")
    starts_at = slot.starts_at if slot.starts_at.tzinfo else slot.starts_at.replace(tzinfo=timezone.utc)
    if starts_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=409, detail="This availability slot is in the past")
    doctor = db.get(DoctorProfile, slot.doctor_id)
    doctor_user = db.get(User, doctor.user_id) if doctor else None
    if doctor is None or doctor_user is None or not doctor_user.is_active:
        raise HTTPException(status_code=409, detail="Doctor is not available")
    appointment = Appointment(patient_id=current_user.id, doctor_id=doctor.id, slot_id=slot.id, scheduled_start=slot.starts_at, scheduled_end=slot.ends_at, reason=data.reason, status="scheduled")
    db.add(appointment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This appointment slot has already been booked")
    db.refresh(appointment)
    return _appointment_response(db, appointment)

@router.get("/me", response_model=list[AppointmentResponse])
def list_my_appointments(current_user: User = Depends(require_roles("patient")), db: Session = Depends(get_db)):
    items = db.scalars(select(Appointment).where(Appointment.patient_id == current_user.id).order_by(Appointment.scheduled_start.desc())).all()
    return [_appointment_response(db, item) for item in items]

@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(appointment_id: int, current_user: User = Depends(require_roles("patient")), db: Session = Depends(get_db)):
    appointment = db.scalar(select(Appointment).where(Appointment.id == appointment_id, Appointment.patient_id == current_user.id).with_for_update())
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment.status != "scheduled":
        raise HTTPException(status_code=409, detail="Only scheduled appointments can be cancelled")
    appointment.status = "cancelled"
    appointment.cancelled_at = datetime.now(timezone.utc)
    appointment.slot_id = None
    db.commit(); db.refresh(appointment)
    return _appointment_response(db, appointment)
