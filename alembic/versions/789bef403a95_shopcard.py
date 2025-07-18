"""shopcard

Revision ID: 789bef403a95
Revises: 496cbd8d1106
Create Date: 2025-07-03 11:28:48.320323

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '789bef403a95'
down_revision: Union[str, Sequence[str], None] = '496cbd8d1106'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shop_cards',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('shop_card_items',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('shop_card_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('added_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['Product.id'], ),
    sa.ForeignKeyConstraint(['shop_card_id'], ['shop_cards.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('shop_card_items')
    op.drop_table('shop_cards')
    # ### end Alembic commands ###
