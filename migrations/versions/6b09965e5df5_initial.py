"""initial

Revision ID: 6b09965e5df5
Revises:
Create Date: 2026-07-01 00:07:14.443869
"""

from collections.abc import Sequence

revision: str = "6b09965e5df5"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
