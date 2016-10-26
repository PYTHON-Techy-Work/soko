"""empty message

Revision ID: ec34cce59dcb
Revises: 25ca21c14628
Create Date: 2016-10-25 17:10:56.624489

"""

# revision identifiers, used by Alembic.
revision = 'ec34cce59dcb'
down_revision = '25ca21c14628'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('product_reviews')
    op.add_column('product_ratings', sa.Column('product', sa.Integer(), nullable=False))
    op.add_column('product_ratings', sa.Column('rating', sa.Integer(), nullable=False))
    op.add_column('product_ratings', sa.Column('review', sa.String(length=80), nullable=True))
    op.drop_column('product_ratings', 'description')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product_ratings', sa.Column('description', sa.VARCHAR(length=80), autoincrement=False, nullable=True))
    op.drop_column('product_ratings', 'review')
    op.drop_column('product_ratings', 'rating')
    op.drop_column('product_ratings', 'product')
    op.create_table('product_reviews',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('product', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('review', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name=u'product_reviews_pkey')
    )
    ### end Alembic commands ###