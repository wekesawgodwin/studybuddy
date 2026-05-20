"""create_course_tables

Revision ID: 3707269d339c
Revises: 1c47a9f0b811
Create Date: 2026-05-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '3707269d339c'
down_revision = '1c47a9f0b811'
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ── Step 1 — Create user_role enum ───────────────────────────────────
    # We use op.execute with raw SQL to create the enum type directly.
    # This bypasses SQLAlchemy's enum handling entirely and gives us
    # full control over when and how the type is created.
    op.execute(
        "CREATE TYPE user_role AS ENUM ('super_admin', 'admin', 'student')"
    )

    # ── Step 2 — Create table_name enum ──────────────────────────────────
    op.execute("""
        CREATE TYPE table_name AS ENUM (
            'courses',
            'modules',
            'topics',
            'users',
            'enrollments',
            'markdown_documents',
            'llm_generation_jobs',
            'mastery_test_attempts',
            'lives_accounts',
            'gem_accounts',
            'analytics'
        )
    """)

    # ── Step 3 — Create courses table ────────────────────────────────────
    op.create_table(
        'courses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Boolean(), nullable=False,
                  server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=False,
                  server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # ── Step 4 — Create modules table ────────────────────────────────────
    op.create_table(
        'modules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('course_id', postgresql.UUID(as_uuid=True),
                  nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False,
                  server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ['course_id'], ['courses.id'],
            ondelete='CASCADE'
        ),
    )

    # ── Step 5 — Create topics table ──────────────────────────────────────
    op.create_table(
        'topics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('module_id', postgresql.UUID(as_uuid=True),
                  nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False,
                  server_default='0'),
        sa.Column('mastery_required', sa.Boolean(), nullable=False,
                  server_default='true'),
        sa.Column('passing_score', sa.Integer(), nullable=False,
                  server_default='80'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ['module_id'], ['modules.id'],
            ondelete='CASCADE'
        ),
    )

    # ── Step 6 — Add role column to users ─────────────────────────────────
    # Add as nullable first — existing rows cannot have a NOT NULL column
    # added in one step because they have no value yet.
    op.add_column(
        'users',
        sa.Column(
            'role',
            # create_type=False tells SQLAlchemy not to attempt CREATE TYPE
            # since we already created it manually in Step 1 above.
            postgresql.ENUM(
                'super_admin', 'admin', 'student',
                name='user_role',
                create_type=False
            ),
            nullable=True
        )
    )

    # Backfill all existing users with the default role
    op.execute("UPDATE users SET role = 'student' WHERE role IS NULL")

    # Now it is safe to enforce NOT NULL
    op.alter_column('users', 'role', nullable=False)

    # ── Step 7 — Create admin_permissions table ───────────────────────────
    op.create_table(
        'admin_permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            'table_name',
            # create_type=False — type already created in Step 2
            postgresql.ENUM(
                'courses', 'modules', 'topics', 'users', 'enrollments',
                'markdown_documents', 'llm_generation_jobs',
                'mastery_test_attempts', 'lives_accounts',
                'gem_accounts', 'analytics',
                name='table_name',
                create_type=False
            ),
            nullable=False
        ),
        sa.Column('can_create', sa.Boolean(), nullable=False,
                  server_default='false'),
        sa.Column('can_read', sa.Boolean(), nullable=False,
                  server_default='false'),
        sa.Column('can_update', sa.Boolean(), nullable=False,
                  server_default='false'),
        sa.Column('can_delete', sa.Boolean(), nullable=False,
                  server_default='false'),
        sa.Column('granted_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'],
            ondelete='CASCADE'
        ),
    )


def downgrade() -> None:
    # Reverse in the opposite order of creation

    op.drop_table('admin_permissions')
    op.drop_table('topics')
    op.drop_table('modules')
    op.drop_table('courses')
    op.drop_column('users', 'role')

    # Drop enum types last since columns depended on them
    op.execute("DROP TYPE IF EXISTS table_name")
    op.execute("DROP TYPE IF EXISTS user_role")