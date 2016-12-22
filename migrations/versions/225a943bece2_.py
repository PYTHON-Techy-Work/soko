"""empty message

Revision ID: 225a943bece2
Revises: 316b78e292ea
Create Date: 2016-12-22 10:19:12.607954

"""

# revision identifiers, used by Alembic.
revision = '225a943bece2'
down_revision = '316b78e292ea'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('profile_photo', sa.String(length=150), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'profile_photo')
    ### end Alembic commands ###
