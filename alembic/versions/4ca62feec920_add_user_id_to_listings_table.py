"""Add user_id to listings table

Revision ID: 4ca62feec920
Revises: 776bb1a6e9e9
Create Date: 2025-07-22 12:12:27.587147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ca62feec920'
down_revision: Union[str, None] = '776bb1a6e9e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First, create a default admin user if none exists
    connection = op.get_bind()
    
    # Check if admin user exists
    result = connection.execute(sa.text("SELECT COUNT(*) FROM users WHERE username = 'admin'"))
    admin_count = result.scalar()
    
    if admin_count == 0:
        # Create default admin user
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("admin123")
        
        connection.execute(sa.text(
            "INSERT INTO users (email, username, hashed_password, full_name, is_active, is_admin) "
            "VALUES ('admin@localhost', 'admin', :hashed_password, 'Administrator', 1, 1)"
        ), {"hashed_password": hashed_password})
    
    # Get the admin user ID
    result = connection.execute(sa.text("SELECT id FROM users WHERE username = 'admin'"))
    admin_id = result.scalar()
    
    # Add user_id column with default value (admin user id)
    op.add_column('listings', sa.Column('user_id', sa.Integer(), nullable=False, server_default=str(admin_id)))
    
    # Create foreign key constraint
    op.create_foreign_key('fk_listings_user_id', 'listings', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_listings_user_id', 'listings', type_='foreignkey')
    op.drop_column('listings', 'user_id')
