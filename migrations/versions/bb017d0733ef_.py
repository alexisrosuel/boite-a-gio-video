"""empty message

Revision ID: bb017d0733ef
Revises: 
Create Date: 2021-11-12 16:31:51.711302

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb017d0733ef'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('video_file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=80), nullable=False),
    sa.Column('date_added', sa.DateTime(), nullable=False),
    sa.Column('nb_lecture', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=80), nullable=False),
    sa.Column('file', sa.LargeBinary(), nullable=False),
    sa.Column('transcription', sa.String(length=1000), nullable=True),
    sa.Column('user_id', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('filename'),
    sa.UniqueConstraint('title')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('video_file')
    op.drop_table('user')
    # ### end Alembic commands ###
