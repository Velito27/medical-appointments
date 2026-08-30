"""add login history

Revision ID: c2f11e8b9a44
Revises: a71f6ce7b8d2
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c2f11e8b9a44"
down_revision: Union[str, Sequence[str], None] = "a71f6ce7b8d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "login_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "logged_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_login_history_user_id", "login_history", ["user_id"])
    op.create_index("ix_login_history_logged_at", "login_history", ["logged_at"])


def downgrade() -> None:
    op.drop_index("ix_login_history_logged_at", table_name="login_history")
    op.drop_index("ix_login_history_user_id", table_name="login_history")
    op.drop_table("login_history")
