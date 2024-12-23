"""init2

Revision ID: 80e92282107d
Revises: b799c877e080
Create Date: 2024-12-23 16:13:05.378925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '80e92282107d'
down_revision: Union[str, None] = 'b799c877e080'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('useraction', sa.Column('shareIds', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.drop_column('useraction', 'shareCount')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('useraction', sa.Column('shareCount', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('useraction', 'shareIds')
    # ### end Alembic commands ###
