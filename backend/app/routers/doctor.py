from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.dependencies import get_current_doctor_profile, get_db
from app.models.appointment import Appointment
from app.models.availability import AvailabilitySlot
from app.models.doctor import DoctorProfile
from app.routers.appointments import _appointment_response
from app.schemas import AppointmentResponse, AppointmentStatusUpdate, AvailabilityCreate, AvailabilityResponse

router = APIRouter(prefix="/doctor", tags=["Doctor dashboard"])

def aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=ZoneInfo("America/Lima"))
    return value.astimezone(timezone.utc)

@router.get("/slots", response_model=list[AvailabilityResponse])
def list_my_slots(include_past: bool = Query(default=False), doctor: DoctorProfile = Depends(get_current_doctor_profile), db: Session = Depends(get_db)):
    stmt = select(AvailabilitySlot).where(AvailabilitySlot.doctor_id == doctor.id).order_by(AvailabilitySlot.starts_at)
    if not include_past:
        stmt = stmt.where(AvailabilitySlot.ends_at >= datetime.now(timezone.utc))
    result=[]
    for slot in db.scalars(stmt).all():
        booked = bool(db.scalar(select(exists().where(Appointment.slot_id == slot.id))))
        result.append(AvailabilityResponse(id=slot.id, doctor_id=slot.doctor_id, starts_at=slot.starts_at, ends_at=slot.ends_at, is_active=slot.is_active, is_booked=booked))
    return result

@router.post("/slots", response_model=AvailabilityResponse, status_code=status.HTTP_201_CREATED)
def create_slot(data: AvailabilityCreate, doctor: DoctorProfile = Depends(get_current_doctor_profile), db: Session = Depends(get_db)):
    starts_at, ends_at = aware(data.starts_at), aware(data.ends_at)
    if starts_at <= datetime.now(timezone.utc) or ends_at <= starts_at:
        raise HTTPException(status_code=422, detail="Availability must be a valid future range")
    overlap = db.scalar(select(AvailabilitySlot).where(AvailabilitySlot.doctor_id == doctor.id, AvailabilitySlot.is_active.is_(True), AvailabilitySlot.starts_at < ends_at, AvailabilitySlot.ends_at > starts_at))
    if overlap:
        raise HTTPException(status_code=409, detail="This availability overlaps another slot")
    slot = AvailabilitySlot(doctor_id=doctor.id, starts_at=starts_at, ends_at=ends_at)
    db.add(slot)
    try: db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(status_code=409, detail="This availability slot already exists")
    db.refresh(slot)
    return AvailabilityResponse(id=slot.id, doctor_id=slot.doctor_id, starts_at=slot.starts_at, ends_at=slot.ends_at, is_active=slot.is_active, is_booked=False)

@router.delete("/slots/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
def disable_slot(slot_id: int, doctor: DoctorProfile = Depends(get_current_doctor_profile), db: Session = Depends(get_db)):
    slot = db.scalar(select(AvailabilitySlot).where(AvailabilitySlot.id == slot_id, AvailabilitySlot.doctor_id == doctor.id))
    if slot is None: raise HTTPException(status_code=404, detail="Availability slot not found")
    if db.scalar(select(Appointment).where(Appointment.slot_id == slot.id)): raise HTTPException(status_code=409, detail="A booked slot cannot be disabled")
    slot.is_active=False; db.commit()

@router.get("/appointments", response_model=list[AppointmentResponse])
def list_doctor_appointments(appointment_status: str | None = Query(default=None, alias="status"), doctor: DoctorProfile = Depends(get_current_doctor_profile), db: Session = Depends(get_db)):
    stmt=select(Appointment).where(Appointment.doctor_id==doctor.id).order_by(Appointment.scheduled_start)
    if appointment_status: stmt=stmt.where(Appointment.status==appointment_status)
    return [_appointment_response(db,a) for a in db.scalars(stmt).all()]

@router.patch("/appointments/{appointment_id}", response_model=AppointmentResponse)
def update_appointment_status(appointment_id:int, data:AppointmentStatusUpdate, doctor:DoctorProfile=Depends(get_current_doctor_profile), db:Session=Depends(get_db)):
    appointment=db.scalar(select(Appointment).where(Appointment.id==appointment_id, Appointment.doctor_id==doctor.id).with_for_update())
    if appointment is None: raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment.status!="scheduled": raise HTTPException(status_code=409, detail="Only scheduled appointments can be updated")
    if data.status=="cancelled": appointment.cancelled_at=datetime.now(timezone.utc); appointment.slot_id=None
    appointment.status=data.status; db.commit(); db.refresh(appointment)
    return _appointment_response(db, appointment)
