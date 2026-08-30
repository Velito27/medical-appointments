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

DEFAULT_SPECIALTIES = [
    ("Medicina General", "Atención médica general y primera evaluación."),
    ("Cardiología", "Evaluación y seguimiento de la salud cardiovascular."),
    ("Pediatría", "Atención médica para niños y adolescentes."),
]

DEMO_DOCTORS = [
    {
        "email": "doctor@example.com",
        "password": "Doctor123!",
        "full_name": "Dra. Demo",
        "specialty": "Medicina General",
        "license_number": "DEMO-001",
        "bio": "Médica de medicina general.",
    },
    {
        "email": "cardiologia@example.com",
        "password": "Doctor123!",
        "full_name": "Dr. Carlos Ruiz",
        "specialty": "Cardiología",
        "license_number": "CARD-001",
        "bio": "Médico especialista en cardiología.",
    },
    {
        "email": "pediatria@example.com",
        "password": "Doctor123!",
        "full_name": "Dra. Ana Torres",
        "specialty": "Pediatría",
        "license_number": "PED-001",
        "bio": "Médica especialista en pediatría.",
    },
]


def get_or_create_user(db, email, password, role):
    email = email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user:
        return user

    user = User(
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.flush()
    return user


def get_or_create_doctor(db, data, specialties):
    user = get_or_create_user(
        db,
        data["email"],
        data["password"],
        "doctor",
    )

    profile = db.scalar(
        select(DoctorProfile).where(DoctorProfile.user_id == user.id)
    )

    if profile is None:
        profile = DoctorProfile(
            user_id=user.id,
            specialty_id=specialties[data["specialty"]].id,
            full_name=data["full_name"],
            license_number=data["license_number"],
            bio=data["bio"],
        )
        db.add(profile)
        db.flush()

    return profile


def create_demo_slots(db, doctor):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date()

    for hour in (9, 10, 11):
        start = datetime(
            tomorrow.year,
            tomorrow.month,
            tomorrow.day,
            hour,
            tzinfo=timezone.utc,
        )
        end = start + timedelta(minutes=45)

        existing = db.scalar(
            select(AvailabilitySlot).where(
                AvailabilitySlot.doctor_id == doctor.id,
                AvailabilitySlot.starts_at == start,
                AvailabilitySlot.ends_at == end,
            )
        )

        if existing is None:
            db.add(
                AvailabilitySlot(
                    doctor_id=doctor.id,
                    starts_at=start,
                    ends_at=end,
                )
            )


def seed():
    db = SessionLocal()

    try:
        get_or_create_user(
            db,
            settings.admin_email,
            settings.admin_password,
            "admin",
        )

        specialties = {}
        for name, description in DEFAULT_SPECIALTIES:
            specialty = db.scalar(
                select(Specialty).where(Specialty.name == name)
            )
            if specialty is None:
                specialty = Specialty(
                    name=name,
                    description=description,
                )
                db.add(specialty)
                db.flush()

            specialties[name] = specialty

        if settings.seed_demo_data:
            get_or_create_user(
                db,
                "patient@example.com",
                "Patient123!",
                "patient",
            )

            for doctor_data in DEMO_DOCTORS:
                doctor = get_or_create_doctor(
                    db,
                    doctor_data,
                    specialties,
                )
                create_demo_slots(db, doctor)

        db.commit()
        print("Seed completed.")

    except IntegrityError:
        db.rollback()
        print("Seed skipped because equivalent data already exists.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
