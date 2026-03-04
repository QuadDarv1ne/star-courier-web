"""
StarCourier Web - Email Service
Сервис для отправки email уведомлений

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
from string import Template
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# EMAIL TEMPLATES
# ============================================================================

EMAIL_TEMPLATES = {
    "welcome": {
        "subject": {
            "ru": "Добро пожаловать в StarCourier!",
            "en": "Welcome to StarCourier!"
        },
        "body": {
            "ru": """
Здравствуйте, {username}!

Добро пожаловать в StarCourier — интерактивную текстовую RPG в космической тематике!

Ваш аккаунт успешно создан. Теперь вы можете:
• Отправиться в захватывающее космическое приключение
• Исследовать таинственные артефакты
• Принимать важные решения, влияющие на судьбу человечества
• Соревноваться с другими игроками в таблице лидеров

Начните своё приключение: {game_url}

Удачи в космических просторах!
Команда StarCourier
            """,
            "en": """
Hello, {username}!

Welcome to StarCourier — an interactive text RPG set in space!

Your account has been successfully created. Now you can:
• Embark on an exciting space adventure
• Explore mysterious artifacts
• Make important decisions affecting humanity's fate
• Compete with other players on the leaderboard

Start your adventure: {game_url}

Good luck in the cosmic vastness!
StarCourier Team
            """
        }
    },
    
    "password_reset": {
        "subject": {
            "ru": "Восстановление пароля StarCourier",
            "en": "StarCourier Password Reset"
        },
        "body": {
            "ru": """
Здравствуйте, {username}!

Вы запросили восстановление пароля для вашего аккаунта StarCourier.

Для установки нового пароля перейдите по ссылке:
{reset_url}

Ссылка действительна в течение 1 часа.

Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо.

Команда StarCourier
            """,
            "en": """
Hello, {username}!

You requested a password reset for your StarCourier account.

To set a new password, follow this link:
{reset_url}

The link is valid for 1 hour.

If you didn't request a password reset, simply ignore this email.

StarCourier Team
            """
        }
    },
    
    "achievement_unlocked": {
        "subject": {
            "ru": "Новое достижение в StarCourier!",
            "en": "New Achievement in StarCourier!"
        },
        "body": {
            "ru": """
Поздравляем, {username}!

Вы разблокировали новое достижение:

🎖️ {achievement_name}
{achievement_description}

Очков: {achievement_points}
Редкость: {achievement_rarity}

Продолжайте исследовать космос!

Команда StarCourier
            """,
            "en": """
Congratulations, {username}!

You've unlocked a new achievement:

🎖️ {achievement_name}
{achievement_description}

Points: {achievement_points}
Rarity: {achievement_rarity}

Keep exploring the cosmos!

StarCourier Team
            """
        }
    },
    
    "game_completed": {
        "subject": {
            "ru": "Игра завершена! StarCourier",
            "en": "Game Completed! StarCourier"
        },
        "body": {
            "ru": """
Поздравляем, {username}!

Вы завершили игру StarCourier!

📊 Ваша статистика:
• Концовка: {ending_type}
• Очки: {score}
• Выборов сделано: {choices_made}
• Время игры: {playtime}

🏆 Ваше место в таблице лидеров: {rank}

Сыграйте ещё раз, чтобы открыть другие концовки!

Команда StarCourier
            """,
            "en": """
Congratulations, {username}!

You've completed StarCourier!

📊 Your Statistics:
• Ending: {ending_type}
• Score: {score}
• Choices made: {choices_made}
• Playtime: {playtime}

🏆 Your leaderboard rank: {rank}

Play again to unlock different endings!

StarCourier Team
            """
        }
    },
    
    "weekly_report": {
        "subject": {
            "ru": "Ваш еженедельный отчёт StarCourier",
            "en": "Your Weekly StarCourier Report"
        },
        "body": {
            "ru": """
Здравствуйте, {username}!

Ваша статистика за неделю:

🎮 Игр сыграно: {games_played}
⏱️ Время в игре: {playtime}
🎖️ Достижений получено: {achievements_unlocked}
📊 Очков заработано: {score_earned}

🏆 Текущий рейтинг: #{rank}

Продолжайте приключение!

Команда StarCourier
            """,
            "en": """
Hello, {username}!

Your weekly statistics:

🎮 Games played: {games_played}
⏱️ Time played: {playtime}
🎖️ Achievements unlocked: {achievements_unlocked}
📊 Points earned: {score_earned}

🏆 Current rank: #{rank}

Keep adventuring!

StarCourier Team
            """
        }
    }
}


# ============================================================================
# EMAIL SERVICE CLASS
# ============================================================================

class EmailService:
    """Сервис для отправки email уведомлений"""
    
    def __init__(self):
        self.enabled = settings.email_enabled
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.from_name = settings.smtp_from_name
        self._executor = ThreadPoolExecutor(max_workers=3)
    
    def _create_connection(self) -> Optional[smtplib.SMTP]:
        """Создание SMTP соединения"""
        if not self.enabled:
            return None
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            return server
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {e}")
            return None
    
    def _render_template(
        self, 
        template_name: str, 
        language: str = "ru",
        **kwargs
    ) -> tuple[str, str]:
        """Рендеринг email шаблона"""
        template = EMAIL_TEMPLATES.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Получение темы и тела на нужном языке
        subject = template["subject"].get(language, template["subject"]["en"])
        body = template["body"].get(language, template["body"]["en"])
        
        # Подстановка параметров
        subject = subject.format(**kwargs)
        body = body.format(**kwargs)
        
        return subject, body
    
    def _send_email_sync(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: List[Dict] = None
    ) -> bool:
        """Синхронная отправка email"""
        if not self.enabled:
            logger.info(f"Email disabled. Would send to {to_email}: {subject}")
            return True
        
        try:
            # Создание сообщения
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            
            # Добавление текстовой версии
            msg.attach(MIMEText(body, "plain", "utf-8"))
            
            # Добавление HTML версии
            if html_body:
                msg.attach(MIMEText(html_body, "html", "utf-8"))
            
            # Добавление вложений
            if attachments:
                for attachment in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment["content"])
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={attachment['filename']}"
                    )
                    msg.attach(part)
            
            # Отправка
            server = self._create_connection()
            if server:
                server.sendmail(self.from_email, to_email, msg.as_string())
                server.quit()
                logger.info(f"Email sent to {to_email}: {subject}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: List[Dict] = None
    ) -> bool:
        """Асинхронная отправка email"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._send_email_sync,
            to_email,
            subject,
            body,
            html_body,
            attachments
        )
    
    async def send_template_email(
        self,
        to_email: str,
        template_name: str,
        language: str = "ru",
        **kwargs
    ) -> bool:
        """Отправка email по шаблону"""
        try:
            subject, body = self._render_template(template_name, language, **kwargs)
            return await self.send_email(to_email, subject, body)
        except Exception as e:
            logger.error(f"Failed to send template email: {e}")
            return False
    
    # ========================================================================
    # КОНКРЕТНЫЕ МЕТОДЫ ОТПРАВКИ
    # ========================================================================
    
    async def send_welcome_email(
        self,
        to_email: str,
        username: str,
        language: str = "ru"
    ) -> bool:
        """Отправка приветственного письма"""
        game_url = settings.frontend_url
        return await self.send_template_email(
            to_email,
            "welcome",
            language,
            username=username,
            game_url=game_url
        )
    
    async def send_password_reset_email(
        self,
        to_email: str,
        username: str,
        reset_token: str,
        language: str = "ru"
    ) -> bool:
        """Отправка письма для восстановления пароля"""
        reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"
        return await self.send_template_email(
            to_email,
            "password_reset",
            language,
            username=username,
            reset_url=reset_url
        )
    
    async def send_achievement_email(
        self,
        to_email: str,
        username: str,
        achievement_name: str,
        achievement_description: str,
        achievement_points: int,
        achievement_rarity: str,
        language: str = "ru"
    ) -> bool:
        """Отправка уведомления о достижении"""
        return await self.send_template_email(
            to_email,
            "achievement_unlocked",
            language,
            username=username,
            achievement_name=achievement_name,
            achievement_description=achievement_description,
            achievement_points=achievement_points,
            achievement_rarity=achievement_rarity
        )
    
    async def send_game_completed_email(
        self,
        to_email: str,
        username: str,
        ending_type: str,
        score: int,
        choices_made: int,
        playtime: str,
        rank: int,
        language: str = "ru"
    ) -> bool:
        """Отправка уведомления о завершении игры"""
        return await self.send_template_email(
            to_email,
            "game_completed",
            language,
            username=username,
            ending_type=ending_type,
            score=score,
            choices_made=choices_made,
            playtime=playtime,
            rank=rank
        )
    
    async def send_weekly_report_email(
        self,
        to_email: str,
        username: str,
        games_played: int,
        playtime: str,
        achievements_unlocked: int,
        score_earned: int,
        rank: int,
        language: str = "ru"
    ) -> bool:
        """Отправка еженедельного отчёта"""
        return await self.send_template_email(
            to_email,
            "weekly_report",
            language,
            username=username,
            games_played=games_played,
            playtime=playtime,
            achievements_unlocked=achievements_unlocked,
            score_earned=score_earned,
            rank=rank
        )
    
    def shutdown(self):
        """Завершение работы сервиса"""
        self._executor.shutdown(wait=True)


# Глобальный экземпляр
email_service = EmailService()
