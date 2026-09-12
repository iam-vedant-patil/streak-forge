"""prevent duplicate task completions

Revision ID: 43caefc9093f
Revises: ff777b0bd22c
Create Date: 2026-09-12 19:20:31.162586

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43caefc9093f'
down_revision: Union[str, Sequence[str], None] = 'ff777b0bd22c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("task_completions") as batch_op:
        batch_op.create_unique_constraint(
            "uq_task_completion_date",
            ["task_id", "completion_date"],
        )

def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("task_completions") as batch_op:
        batch_op.drop_constraint(
            "uq_task_completion_date",
            type_="unique",
        )
