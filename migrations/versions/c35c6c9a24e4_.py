"""empty message

Revision ID: c35c6c9a24e4
Revises: 7bb48e4a3220
Create Date: 2023-03-09 15:27:18.676087

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c35c6c9a24e4'
down_revision = '7bb48e4a3220'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('editor_fees',
    sa.Column('create_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='创建时间'),
    sa.Column('update_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='更新时间'),
    sa.Column('update_cnt', sa.SmallInteger(), server_default=sa.text('1'), nullable=False, comment='更新次数'),
    sa.Column('deleted', sa.Boolean(), server_default=sa.text('0'), nullable=False, comment='删除标记'),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('editorType', sa.Enum('作者', '编辑'), nullable=False),
    sa.Column('editorId', sa.Integer(), nullable=False, comment='作者ID'),
    sa.Column('workId', sa.Integer(), nullable=False, comment='稿件ID'),
    sa.Column('workFee', sa.DECIMAL(precision=10, scale=5), nullable=False, comment='该作者/编辑在该作品中的应付稿酬'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('editor_works', schema=None) as batch_op:
        batch_op.add_column(sa.Column('note', sa.Text(), nullable=True, comment='其他信息'))
        batch_op.drop_column('editorType')
        batch_op.drop_column('editorId')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('editor_works', schema=None) as batch_op:
        batch_op.add_column(sa.Column('editorId', sa.INTEGER(), nullable=False))
        batch_op.add_column(sa.Column('editorType', sa.VARCHAR(length=2), nullable=False))
        batch_op.drop_column('note')

    op.drop_table('editor_fees')
    # ### end Alembic commands ###