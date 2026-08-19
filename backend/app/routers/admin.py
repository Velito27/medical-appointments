from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_roles
from app.models.doctor import DoctorProfile
from app.models.specialty import Specialty
from app.models.user import User
from app.schemas import DoctorCreate, DoctorResponse, DoctorUpdate, SpecialtyCreate, SpecialtyResponse, SpecialtyUpdate, UserActiveUpdate, UserResponse
from app.security import hash_password

router=APIRouter(prefix="/admin",tags=["Admin dashboard"])

def doctor_response(db,profile):
    user=db.get(User,profile.user_id); specialty=db.get(Specialty,profile.specialty_id)
    if user is None or specialty is None: raise HTTPException(status_code=500,detail="Doctor references invalid data")
    return DoctorResponse(id=profile.id,user_id=user.id,email=user.email,full_name=profile.full_name,specialty_id=specialty.id,specialty_name=specialty.name,license_number=profile.license_number,bio=profile.bio,is_active=user.is_active)

@router.get("/users",response_model=list[UserResponse])
def list_users(_admin:User=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    return db.scalars(select(User).order_by(User.created_at.desc())).all()

@router.patch("/users/{user_id}/active",response_model=UserResponse)
def set_user_active(user_id:int,data:UserActiveUpdate,current_admin:User=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    if user_id==current_admin.id and not data.is_active: raise HTTPException(status_code=409,detail="You cannot deactivate your own admin account")
    user=db.get(User,user_id)
    if user is None: raise HTTPException(status_code=404,detail="User not found")
    user.is_active=data.is_active; db.commit(); db.refresh(user); return user

@router.post("/specialties",response_model=SpecialtyResponse,status_code=status.HTTP_201_CREATED)
def create_specialty(data:SpecialtyCreate,_admin:User=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    specialty=Specialty(name=data.name.strip(),description=data.description); db.add(specialty)
    try: db.commit()
    except IntegrityError: db.rollback(); raise HTTPException(status_code=409,detail="Specialty already exists")
    db.refresh(specialty); return specialty

@router.patch("/specialties/{specialty_id}",response_model=SpecialtyResponse)
def update_specialty(specialty_id:int,data:SpecialtyUpdate,_admin:User=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    specialty=db.get(Specialty,specialty_id)
    if specialty is None: raise HTTPException(status_code=404,detail="Specialty not found")
    if data.name is not None: specialty.name=data.name.strip()
    if data.description is not None: specialty.description=data.description
    if data.is_active is not None: specialty.is_active=data.is_active
    try: db.commit()
    except IntegrityError: db.rollback(); raise HTTPException(status_code=409,detail="Specialty name already exists")
    db.refresh(specialty); return specialty

@router.delete("/specialties/{specialty_id}",response_model=SpecialtyResponse)
def deactivate_specialty(specialty_id:int,_admin:User=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    specialty=db.get(Specialty,specialty_id)
    if specialty is None: raise HTTPException(status_code=404,detail="Specialty not found")
    specialty.is_active=False; db.commit(); db.refresh(specialty); return specialty

@router.get("/doctors",response_model=list[DoctorResponse])
def list_doctors(_admin:User=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    return [doctor_response(db,p) for p in db.scalars(select(DoctorProfile).order_by(DoctorProfile.full_name)).all()]

@router.post("/doctors",response_model=DoctorResponse,status_code=status.HTTP_201_CREATED)
def create_doctor(data:DoctorCreate,_admin:User=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    specialty=db.get(Specialty,data.specialty_id)
    if specialty is None or not specialty.is_active: raise HTTPException(status_code=404,detail="Specialty not found or inactive")
    email=str(data.email).strip().lower()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(status_code=409,detail="Email already registered")
    user=User(email=email,password_hash=hash_password(data.password),role="doctor"); db.add(user)
    try:
        db.flush(); profile=DoctorProfile(user_id=user.id,specialty_id=data.specialty_id,full_name=data.full_name.strip(),license_number=data.license_number,bio=data.bio); db.add(profile); db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(status_code=409,detail="Doctor could not be created; email or license may already exist")
    db.refresh(profile); return doctor_response(db,profile)

@router.patch("/doctors/{doctor_id}",response_model=DoctorResponse)
def update_doctor(doctor_id:int,data:DoctorUpdate,_admin:User=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    profile=db.get(DoctorProfile,doctor_id)
    if profile is None: raise HTTPException(status_code=404,detail="Doctor not found")
    user=db.get(User,profile.user_id)
    if data.specialty_id is not None:
        specialty=db.get(Specialty,data.specialty_id)
        if specialty is None or not specialty.is_active: raise HTTPException(status_code=404,detail="Specialty not found or inactive")
        profile.specialty_id=data.specialty_id
    if data.full_name is not None: profile.full_name=data.full_name.strip()
    if data.license_number is not None: profile.license_number=data.license_number
    if data.bio is not None: profile.bio=data.bio
    if data.is_active is not None: user.is_active=data.is_active
    try: db.commit()
    except IntegrityError: db.rollback(); raise HTTPException(status_code=409,detail="Doctor data conflicts with an existing record")
    db.refresh(profile); return doctor_response(db,profile)
