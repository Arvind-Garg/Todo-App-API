"""set created_at server defaults

Revision ID: ab0f941e0670
Revises: 
Create Date: 2025-12-28 21:04:55.014170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab0f941e0670'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    #set server_deault for users.created_at, backfill existing NULLs, then make NOT NULL
    op.alter_column('users', 'created_at',
    existing_type=sa.DateTime(),
    server_default=sa.text('now()'),
    existing_nullable=True,
    )
    op.execute ("Update users SET created_at =  now() WHERE created_at IS NULL")
    op.alter_column('users', 'created_at',
         existing_type=sa.DateTime(), 
         nullable=False
         )

    op.alter_column('todos', 'created_at',
        existing_type=sa.DateTime(),
        server_default=sa.text('now()'),
        existing_nullable=True,
    )

    op.execute("Update todos SET created_at =now() WHERE created_at IS NULL")
    op.alter_column('todos', 'created_at', existing_type=sa.DateTime(), nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # remove defaults and allow NULLs again
    op.alter_column('users', 'created_at', 
        existing_type=sa.DateTime(), 
        server_default = None, 
        nullable=True
        )

    op.alter_column('todos', 'created_at',
        existing_type=sa.DateTime(),
        server_default=None,
        nullable=True,
        )

    # ### end Alembic commands ###
