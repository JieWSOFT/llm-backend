"""init3

Revision ID: 3f7a353a4d5e
Revises: 80e92282107d
Create Date: 2024-12-23 16:41:02.623952

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '3f7a353a4d5e'
down_revision: Union[str, None] = '80e92282107d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('useraction', sa.Column('type', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('useraction', sa.Column('toUserId', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.drop_column('useraction', 'shareIds')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('useraction', sa.Column('shareIds', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('useraction', 'toUserId')
    op.drop_column('useraction', 'type')
    # ### end Alembic commands ###