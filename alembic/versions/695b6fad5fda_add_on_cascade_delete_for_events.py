"""Add on cascade delete for events

Revision ID: 695b6fad5fda
Revises: 
Create Date: 2025-05-12 23:10:26.634530

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '695b6fad5fda'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa

def upgrade():
    with op.batch_alter_table("user_events") as batch_op:
        

        # Recreate the foreign key constraints with ON DELETE CASCADE and explicit names
        batch_op.create_foreign_key('fk_user_events_user_email_users', 'users', ['user_email'], ['email'], ondelete='CASCADE')
        batch_op.create_foreign_key('fk_user_events_event_id_events', 'events', ['event_id'], ['id'], ondelete='CASCADE')

def downgrade():
    with op.batch_alter_table("user_events") as batch_op:
        # Drop the new FKs
        batch_op.drop_constraint('fk_user_events_user_email_users', type_='foreignkey')
        batch_op.drop_constraint('fk_user_events_event_id_events', type_='foreignkey')
        # Recreate without ON DELETE CASCADE (assuming that was the original state)
        batch_op.create_foreign_key('fk_user_events_user_email_users', 'users', ['user_email'], ['email'])
        batch_op.create_foreign_key('fk_user_events_event_id_events', 'events', ['event_id'], ['id'])