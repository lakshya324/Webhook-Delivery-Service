"""initial migration

Revision ID: f2f0e11f9090
Revises: 
Create Date: 2023-05-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = 'f2f0e11f9090'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('target_url', sa.String(), nullable=False),
        sa.Column('secret_key', sa.String(), nullable=True),
        sa.Column('event_types', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_subscriptions_id', 'subscriptions', ['id'], unique=True)
    
    # Create webhook_payloads table
    op.create_table(
        'webhook_payloads',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('subscription_id', sa.String(), nullable=True),
        sa.Column('event_type', sa.String(), nullable=True),
        sa.Column('payload', JSON, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_webhook_payloads_id', 'webhook_payloads', ['id'], unique=True)
    op.create_index('ix_webhook_payloads_subscription_id', 'webhook_payloads', ['subscription_id'], unique=False)
    
    # Create delivery_logs table
    op.create_table(
        'delivery_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('webhook_id', sa.String(), nullable=False),
        sa.Column('subscription_id', sa.String(), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('status', sa.String(), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('error_details', sa.Text(), nullable=True),
        sa.Column('attempt_timestamp', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('next_attempt_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['webhook_id'], ['webhook_payloads.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_delivery_logs_webhook_id', 'delivery_logs', ['webhook_id'], unique=False)
    op.create_index('ix_delivery_logs_subscription_id', 'delivery_logs', ['subscription_id'], unique=False)
    op.create_index('ix_delivery_logs_status', 'delivery_logs', ['status'], unique=False)
    op.create_index('ix_delivery_logs_next_attempt_at', 'delivery_logs', ['next_attempt_at'], unique=False)
    op.create_index('ix_delivery_logs_attempt_timestamp', 'delivery_logs', ['attempt_timestamp'], unique=False)


def downgrade():
    op.drop_table('delivery_logs')
    op.drop_table('webhook_payloads')
    op.drop_table('subscriptions')