from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.config import settings
from app.database import SessionLocal
from app.models.availability import AvailabilitySlot
from app.models.doctor import DoctorProfile
from app.models.specialty import Specialty
from app.models.user import User
from app.security import hash_password

DEFAULT_SPECIALTIES=[("Medicina General","Atención médica general y primera evaluación."),("Cardiología","Evaluación y seguimiento de la salud cardiovascular."),("Pediatría","Atención médica para niños y adolescentes.")]

def get_or_create_user(db,email,password,role):
    email=email.strip().lower(); user=db.scalar(select(User).where(User.email==email))
    if user: return user
    user=User(email=email,password_hash=hash_password(password),role=role); db.add(user); db.flush(); return user

def seed():
    db=SessionLocal()
    try:
        get_or_create_user(db,settings.admin_email,settings.admin_password,"admin")
        specs={}
        for name,desc in DEFAULT_SPECIALTIES:
            s=db.scalar(select(Specialty).where(Specialty.name==name))
            if s is None: s=Specialty(name=name,description=desc); db.add(s); db.flush()
            specs[name]=s
        if settings.seed_demo_data:
            du=get_or_create_user(db,"doctor@example.com","Doctor123!","doctor")
            get_or_create_user(db,"patient@example.com","Patient123!","patient")
            p=db.scalar(select(DoctorProfile).where(DoctorProfile.user_id==du.id))
            if p is None: p=DoctorProfile(user_id=du.id,specialty_id=specs["Medicina General"].id,full_name="Dra. Demo",license_number="DEMO-001",bio="Cuenta de demostración para probar el sistema."); db.add(p); db.flush()
            tomorrow=(datetime.now(timezone.utc)+timedelta(days=1)).date()
            for offset in range(3):
                day=tomorrow+timedelta(days=offset)
                for hour in (9,10,11):
                    start=datetime(day.year,day.month,day.day,hour,tzinfo=timezone.utc); end=start+timedelta(minutes=45)
                    if db.scalar(select(AvailabilitySlot).where(AvailabilitySlot.doctor_id==p.id,AvailabilitySlot.starts_at==start,AvailabilitySlot.ends_at==end)) is None: db.add(AvailabilitySlot(doctor_id=p.id,starts_at=start,ends_at=end))
        db.commit(); print("Seed completed.")
    except IntegrityError:
        db.rollback(); print("Seed skipped because equivalent data already exists.")
    finally: db.close()

if __name__=="__main__": seed()
