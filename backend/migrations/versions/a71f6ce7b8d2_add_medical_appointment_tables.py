"""add medical appointment tables

Revision ID: a71f6ce7b8d2
Revises: f5c6afa62fb5
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a71f6ce7b8d2"
down_revision: Union[str, Sequence[str], None] = "f5c6afa62fb5"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("specialties",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))
    op.create_index("ix_specialties_name", "specialties", ["name"], unique=True)
    op.create_table("doctor_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("specialty_id", sa.Integer(), sa.ForeignKey("specialties.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("license_number", sa.String(80), unique=True),
        sa.Column("bio", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))
    op.create_index("ix_doctor_profiles_user_id", "doctor_profiles", ["user_id"], unique=True)
    op.create_index("ix_doctor_profiles_specialty_id", "doctor_profiles", ["specialty_id"])
    op.create_table("availability_slots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("doctor_id", sa.Integer(), sa.ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("ends_at > starts_at", name="ck_availability_valid_range"),
        sa.UniqueConstraint("doctor_id", "starts_at", "ends_at", name="uq_availability_doctor_range"))
    op.create_index("ix_availability_slots_doctor_id", "availability_slots", ["doctor_id"])
    op.create_index("ix_availability_slots_starts_at", "availability_slots", ["starts_at"])
    op.create_table("appointments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("doctor_id", sa.Integer(), sa.ForeignKey("doctor_profiles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("slot_id", sa.Integer(), sa.ForeignKey("availability_slots.id", ondelete="SET NULL"), nullable=True),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.Text()),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("status IN ('scheduled', 'cancelled', 'completed')", name="ck_appointments_status"),
        sa.CheckConstraint("scheduled_end > scheduled_start", name="ck_appointment_valid_range"))
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"])
    op.create_index("ix_appointments_doctor_id", "appointments", ["doctor_id"])
    op.create_index("ix_appointments_slot_id", "appointments", ["slot_id"], unique=True)

def downgrade() -> None:
    op.drop_table("appointments")
    op.drop_table("availability_slots")
    op.drop_table("doctor_profiles")
    op.drop_table("specialties")
