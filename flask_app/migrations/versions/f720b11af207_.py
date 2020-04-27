"""empty message

Revision ID: f720b11af207
Revises: 
Create Date: 2020-04-14 18:38:41.611444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f720b11af207'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('store',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('storetype', sa.String(), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('zipcode', sa.String(length=10), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('website_url', sa.String(), nullable=True),
    sa.Column('logo_url', sa.String(), nullable=True),
    sa.Column('giftcard_url', sa.String(), nullable=True),
    sa.Column('contact_url', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('name', 'address')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('store')
    # ### end Alembic commands ###
