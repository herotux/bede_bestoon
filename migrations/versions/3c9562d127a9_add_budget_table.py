"""add budget table

Revision ID: 3c9562d127a9
Revises: 537705effd24
Create Date: 2024-07-17 09:08:06.422638

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c9562d127a9'
down_revision = '537705effd24'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('budget',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('monthly_budget', sa.Float(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('budget')
    # ### end Alembic commands ###
