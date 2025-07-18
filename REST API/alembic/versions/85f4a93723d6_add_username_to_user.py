"""Add username to User

Revision ID: 85f4a93723d6
Revises: dd3689e3ba14
Create Date: 2025-07-06 17:12:50.140176

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85f4a93723d6'
down_revision: Union[str, None] = 'dd3689e3ba14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_index('ix_contacts_email', table_name='contacts')
    op.drop_index('ix_contacts_id', table_name='contacts')
    op.drop_table('contacts')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contacts',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('first_name', sa.VARCHAR(length=150), nullable=False),
    sa.Column('last_name', sa.VARCHAR(length=150), nullable=False),
    sa.Column('email', sa.VARCHAR(length=150), nullable=False),
    sa.Column('phone_number', sa.VARCHAR(length=50), nullable=True),
    sa.Column('birthday', sa.DATE(), nullable=False),
    sa.Column('additional_info', sa.VARCHAR(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_contacts_id', 'contacts', ['id'], unique=False)
    op.create_index('ix_contacts_email', 'contacts', ['email'], unique=1)
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('email', sa.VARCHAR(length=150), nullable=False),
    sa.Column('password', sa.VARCHAR(length=255), nullable=False),
    sa.Column('refresh_token', sa.VARCHAR(length=255), nullable=True),
    sa.Column('email_verified', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###
