"""add user ownership to tasks

Revision ID: d9a3388acaf8
Revises: 43caefc9093f
Create Date: 2026-09-13 16:15:01.274480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9a3388acaf8'
down_revision: Union[str, Sequence[str], None] = '43caefc9093f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add the column as nullable so existing tasks can be migrated.
    op.add_column(
        'tasks',
        sa.Column('user_id', sa.Integer(), nullable=True),
    )

    # Assign existing tasks to the existing user.
    op.execute("UPDATE tasks SET user_id = 1 WHERE user_id IS NULL")

    # SQLite requires batch mode to safely alter an existing column.
    with op.batch_alter_table('tasks') as batch_op:
        batch_op.alter_column(
            'user_id',
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.create_foreign_key(
            'fk_tasks_user_id_users',
            'users',
            ['user_id'],
            ['id'],
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('tasks') as batch_op:
        batch_op.drop_constraint(
            'fk_tasks_user_id_users',
            type_='foreignkey',
        )
        batch_op.drop_column('user_id')
