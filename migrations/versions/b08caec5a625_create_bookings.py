from collections.abc import Sequence

from alembic import op

"""create bookings

Revision ID: b08caec5a625
Revises:
Create Date: 2026-11-22 20:35:26.386313

"""


# revision identifiers, used by Alembic.
revision: str = "b08caec5a625"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
            CREATE TABLE bookings (
                id UUID PRIMARY KEY,
                lot INTEGER NOT NULL,
                spot INTEGER NOT NULL,
                license_plate TEXT NOT NULL,
                driver TEXT NOT NULL,
                start_time TIMESTAMPTZ NOT NULL,
                end_time TIMESTAMPTZ NOT NULL,
                hourly_rate NUMERIC(10, 2) NOT NULL,
                total NUMERIC(10, 2) NOT NULL,
                status TEXT NOT NULL
            )
            """
    )


def downgrade() -> None:
    op.execute("DROP TABLE bookings")
