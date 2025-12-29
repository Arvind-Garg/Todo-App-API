"""fix boolean_defaults

Revision ID: 197cc5a9f300
Revises: ab0f941e0670
Create Date: 2025-12-30 00:54:19.854596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '197cc5a9f300'
down_revision: Union[str, Sequence[str], None] = 'ab0f941e0670'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    #Backfill: Ensure no NULL exist before we tighten the rules
    op.execute("UPDATE users SET is_active =true where is_active IS NULL")
    op.execute("UPDATE todos SET completed = false where completed IS NULL")
    
    #Fix users table
    op.alter_column('users', 'is_active',
        existing_type=sa.Boolean(),
        server_default=sa.text('true'),
        nullable=False
        )
    
    #Fix todos table
    op.alter_column('todos', 'completed',
        existing_type=sa.Boolean(),
        server_default=sa.text('false'),
        nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    #To undo, we remove the server default and allow Null 
    op.alter_column('todos', 'completed',
        existing_type=sa.Boolean(),
        server_default=None,
        nullable=True)
    op.alter_column('users', 'is_active',
        existing_type=sa.Boolean(),
        server_default=None,
        nullable=True)
