"""Initial database schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Создание начальной схемы базы данных"""
    
    # Таблица пользователей
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('bio', sa.Text, nullable=True),
        sa.Column('games_played', sa.Integer, default=0),
        sa.Column('games_completed', sa.Integer, default=0),
        sa.Column('total_playtime', sa.Integer, default=0),
        sa.Column('achievements_count', sa.Integer, default=0),
        sa.Column('total_score', sa.Integer, default=0),
        sa.Column('language', sa.String(5), default='ru'),
        sa.Column('theme', sa.String(20), default='dark'),
        sa.Column('notifications_enabled', sa.Boolean, default=True),
        sa.Column('sound_enabled', sa.Boolean, default=True),
        sa.Column('music_volume', sa.Integer, default=80),
        sa.Column('sfx_volume', sa.Integer, default=100),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('is_premium', sa.Boolean, default=False),
        sa.Column('last_login', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_users_username_lower', 'users', ['username'])
    op.create_index('ix_users_email_lower', 'users', ['email'])
    
    # Таблица статистики игроков
    op.create_table(
        'player_stats',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('player_id', sa.String(36), unique=True, nullable=False),
        sa.Column('current_scene', sa.String(100), default='start'),
        sa.Column('stats', sa.JSON, default=dict),
        sa.Column('relationships', sa.JSON, default=dict),
        sa.Column('inventory', sa.JSON, default=list),
        sa.Column('flags', sa.JSON, default=dict),
        sa.Column('choices_made', sa.Integer, default=0),
        sa.Column('visited_scenes', sa.JSON, default=list),
        sa.Column('achievements_unlocked', sa.JSON, default=list),
        sa.Column('playtime', sa.Integer, default=0),
        sa.Column('ending_type', sa.String(50), nullable=True),
        sa.Column('score', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_player_stats_player_id', 'player_stats', ['player_id'])
    
    # Таблица игровых сессий
    op.create_table(
        'game_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('player_stats_id', sa.String(36), sa.ForeignKey('player_stats.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('current_scene', sa.String(100), default='start'),
        sa.Column('started_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('last_activity', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('duration_seconds', sa.Integer, default=0),
        sa.Column('ending_type', sa.String(50), nullable=True),
        sa.Column('score', sa.Integer, default=0),
        sa.Column('choices_count', sa.Integer, default=0),
        sa.Column('device_info', sa.JSON, default=dict),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
    )
    op.create_index('ix_game_sessions_user_status', 'game_sessions', ['user_id', 'status'])
    op.create_index('ix_game_sessions_started', 'game_sessions', ['started_at'])
    
    # Таблица достижений пользователей
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('achievement_id', sa.String(100), nullable=False),
        sa.Column('unlocked_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('scene', sa.String(100), nullable=True),
        sa.Column('progress', sa.Integer, default=100),
    )
    op.create_index('ix_user_achievements_user_achievement', 'user_achievements', ['user_id', 'achievement_id'], unique=True)
    
    # Таблица событий аналитики
    op.create_table(
        'analytics_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('game_sessions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_name', sa.String(100), nullable=False),
        sa.Column('event_category', sa.String(50), default='gameplay'),
        sa.Column('event_data', sa.JSON, default=dict),
        sa.Column('scene', sa.String(100), nullable=True),
        sa.Column('choice_id', sa.String(100), nullable=True),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('device_type', sa.String(20), nullable=True),
        sa.Column('browser', sa.String(50), nullable=True),
        sa.Column('os', sa.String(50), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
    )
    op.create_index('ix_analytics_events_type', 'analytics_events', ['event_type'])
    op.create_index('ix_analytics_events_timestamp', 'analytics_events', ['timestamp'])
    op.create_index('ix_analytics_events_type_timestamp', 'analytics_events', ['event_type', 'timestamp'])
    op.create_index('ix_analytics_events_user_timestamp', 'analytics_events', ['user_id', 'timestamp'])
    
    # Таблица для rate limiting
    op.create_table(
        'rate_limits',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('key', sa.String(255), unique=True, nullable=False),
        sa.Column('count', sa.Integer, default=1),
        sa.Column('reset_at', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_rate_limits_key', 'rate_limits', ['key'])
    
    # Таблица лидеров
    op.create_table(
        'leaderboard_entries',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('rank', sa.Integer, nullable=False),
        sa.Column('score', sa.Integer, default=0, nullable=False),
        sa.Column('games_completed', sa.Integer, default=0),
        sa.Column('total_playtime', sa.Integer, default=0),
        sa.Column('achievements_count', sa.Integer, default=0),
        sa.Column('last_updated', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_leaderboard_rank', 'leaderboard_entries', ['rank'])
    op.create_index('ix_leaderboard_score', 'leaderboard_entries', ['score'])
    
    # Таблица кэшированного контента игры
    op.create_table(
        'game_content',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('content_type', sa.String(20), nullable=False),
        sa.Column('content_id', sa.String(100), nullable=False),
        sa.Column('content_data', sa.JSON, nullable=False),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_game_content_type_id', 'game_content', ['content_type', 'content_id'], unique=True)


def downgrade() -> None:
    """Откат начальной схемы"""
    op.drop_table('game_content')
    op.drop_table('leaderboard_entries')
    op.drop_table('rate_limits')
    op.drop_table('analytics_events')
    op.drop_table('user_achievements')
    op.drop_table('game_sessions')
    op.drop_table('player_stats')
    op.drop_table('users')
