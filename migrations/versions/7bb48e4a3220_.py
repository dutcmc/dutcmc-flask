"""empty message

Revision ID: 7bb48e4a3220
Revises: 9d4c83896927
Create Date: 2023-03-06 19:27:42.814952

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bb48e4a3220'
down_revision = '9d4c83896927'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('editor_list', schema=None) as batch_op:
        batch_op.drop_column('editor')

    with op.batch_alter_table('enroll_depts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deptInfo', sa.Text(), nullable=True, comment='部门简介'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('enroll_depts', schema=None) as batch_op:
        batch_op.drop_column('deptInfo')

    with op.batch_alter_table('editor_list', schema=None) as batch_op:
        batch_op.add_column(sa.Column('editor', sa.VARCHAR(length=20), nullable=False))

    # ### end Alembic commands ###