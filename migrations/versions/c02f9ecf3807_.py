"""empty message

Revision ID: c02f9ecf3807
Revises: 3ab7bbd11dfd
Create Date: 2023-03-26 20:59:55.052156

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c02f9ecf3807'
down_revision = '3ab7bbd11dfd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ar_model',
    sa.Column('create_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='创建时间'),
    sa.Column('update_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='更新时间'),
    sa.Column('update_cnt', sa.SmallInteger(), server_default=sa.text('1'), nullable=False, comment='更新次数'),
    sa.Column('deleted', sa.Boolean(), server_default=sa.text('0'), nullable=False, comment='删除标记'),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('assetId', sa.String(length=64), nullable=False, comment='模型的AssetID, 必须唯一'),
    sa.Column('name', sa.String(length=64), nullable=False, comment='模型的名称'),
    sa.Column('author', sa.String(length=128), nullable=True, comment='模型提供者'),
    sa.Column('url', sa.Text(), nullable=True, comment='模型对应的URL, 建议使用阿里云OSS的外链'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('assetId')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ar_model')
    # ### end Alembic commands ###
