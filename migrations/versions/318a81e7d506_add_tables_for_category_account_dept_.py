"""add tables for Category Account Dept and Credit

Revision ID: 318a81e7d506
Revises: 2f8801525999
Create Date: 2024-07-18 09:44:05.782456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '318a81e7d506'
down_revision = '2f8801525999'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('debt',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('person', sa.String(length=50), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('credit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('person', sa.String(length=20), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['person'], ['persons.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('expense', schema=None) as batch_op:
        batch_op.alter_column('person',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)

    with op.batch_alter_table('income', schema=None) as batch_op:
        batch_op.alter_column('person',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('income', schema=None) as batch_op:
        batch_op.alter_column('person',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('expense', schema=None) as batch_op:
        batch_op.alter_column('person',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)

    op.drop_table('credit')
    op.drop_table('category')
    op.drop_table('account')
    op.drop_table('debt')
    # ### end Alembic commands ###
