"""
StarCourier Web - Backup Service
Сервис автоматического резервного копирования базы данных

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import os
import logging
import shutil
import gzip
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

from app.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# BACKUP CONFIGURATION
# ============================================================================

BACKUP_DIR = Path(__file__).parent.parent.parent / "backups"
BACKUP_RETENTION_DAYS = 30  # Хранить бэкапы 30 дней
BACKUP_RETENTION_COUNT = 50  # Максимум 50 бэкапов
BACKUP_COMPRESS = True  # Сжимать бэкапы


# ============================================================================
# BACKUP SERVICE
# ============================================================================

class BackupService:
    """Сервис резервного копирования"""
    
    def __init__(
        self,
        backup_dir: Path = BACKUP_DIR,
        retention_days: int = BACKUP_RETENTION_DAYS,
        retention_count: int = BACKUP_RETENTION_COUNT,
        compress: bool = BACKUP_COMPRESS
    ):
        self.backup_dir = backup_dir
        self.retention_days = retention_days
        self.retention_count = retention_count
        self.compress = compress
        self._scheduler_task = None
    
    def _get_db_path(self) -> Optional[Path]:
        """Получение пути к файлу базы данных"""
        if settings.database_type != "sqlite":
            return None
        
        db_url = settings.database_url
        if db_url.startswith("sqlite:///"):
            return Path(db_url.replace("sqlite:///", ""))
        elif db_url.startswith("sqlite://"):
            return Path(db_url.replace("sqlite://", ""))
        
        return None
    
    def _ensure_backup_dir(self):
        """Создание директории для бэкапов"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_backup_filename(self, timestamp: datetime = None) -> str:
        """Генерация имени файла бэкапа"""
        ts = timestamp or datetime.utcnow()
        ts_str = ts.strftime("%Y%m%d_%H%M%S")
        extension = ".db.gz" if self.compress else ".db"
        return f"starcourier_backup_{ts_str}{extension}"
    
    async def create_backup(
        self, 
        description: str = None,
        backup_type: str = "manual"
    ) -> Dict[str, Any]:
        """
        Создание резервной копии базы данных
        
        Args:
            description: Описание бэкапа
            backup_type: Тип бэкапа (manual, scheduled, before_migration)
        
        Returns:
            Информация о созданном бэкапе
        """
        db_path = self._get_db_path()
        
        if not db_path or not db_path.exists():
            return {
                "success": False,
                "error": "Database file not found or not SQLite"
            }
        
        self._ensure_backup_dir()
        
        timestamp = datetime.utcnow()
        backup_filename = self._get_backup_filename(timestamp)
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Копирование и сжатие
            if self.compress:
                with open(db_path, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(db_path, backup_path)
            
            # Получение размера
            backup_size = backup_path.stat().st_size
            
            # Создание метаданных
            metadata = {
                "filename": backup_filename,
                "timestamp": timestamp.isoformat(),
                "type": backup_type,
                "description": description,
                "size_bytes": backup_size,
                "size_human": self._format_size(backup_size),
                "database_size": db_path.stat().st_size,
                "compressed": self.compress,
                "version": settings.app_version
            }
            
            # Сохранение метаданных
            metadata_path = backup_path.with_suffix(".json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Backup created: {backup_filename} ({self._format_size(backup_size)})")
            
            return {
                "success": True,
                "backup": metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def restore_backup(self, backup_filename: str) -> Dict[str, Any]:
        """
        Восстановление из резервной копии
        
        Args:
            backup_filename: Имя файла бэкапа
        
        Returns:
            Результат восстановления
        """
        db_path = self._get_db_path()
        
        if not db_path:
            return {
                "success": False,
                "error": "Database path not found"
            }
        
        backup_path = self.backup_dir / backup_filename
        
        if not backup_path.exists():
            return {
                "success": False,
                "error": f"Backup file not found: {backup_filename}"
            }
        
        try:
            # Создание бэкапа текущей базы перед восстановлением
            if db_path.exists():
                pre_restore_backup = await self.create_backup(
                    description="Auto-backup before restore",
                    backup_type="pre_restore"
                )
                logger.info(f"📦 Pre-restore backup created")
            
            # Восстановление
            if backup_filename.endswith('.gz'):
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(db_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, db_path)
            
            logger.info(f"✅ Database restored from: {backup_filename}")
            
            return {
                "success": True,
                "restored_from": backup_filename,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """Получение списка всех бэкапов"""
        self._ensure_backup_dir()
        
        backups = []
        
        for backup_file in self.backup_dir.glob("starcourier_backup_*.db*"):
            if backup_file.suffix in [".db", ".gz"]:
                metadata_path = backup_file.with_suffix(".json") if backup_file.suffix == ".db" else backup_file.with_suffix(".db.json")
                
                if metadata_path.exists():
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    except Exception:
                        metadata = {}
                else:
                    metadata = {}
                
                backups.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "size": backup_file.stat().st_size,
                    "created_at": datetime.fromtimestamp(
                        backup_file.stat().st_mtime
                    ).isoformat(),
                    **metadata
                })
        
        # Сортировка по дате (новые первыми)
        backups.sort(key=lambda x: x.get("timestamp", x.get("created_at", "")), reverse=True)
        
        return backups
    
    async def cleanup_old_backups(self) -> Dict[str, Any]:
        """
        Удаление старых бэкапов согласно политике хранения
        
        Returns:
            Информация об удалённых бэкапах
        """
        self._ensure_backup_dir()
        
        backups = self.list_backups()
        deleted = []
        
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        
        for backup in backups:
            should_delete = False
            reason = None
            
            # Проверка по дате
            backup_date = datetime.fromisoformat(backup.get("timestamp", backup.get("created_at", "")))
            if backup_date < cutoff_date:
                should_delete = True
                reason = "older_than_retention_days"
            
            # Проверка по количеству (если превышен лимит)
            if len(backups) - len(deleted) > self.retention_count:
                if backup not in [b for b in backups[:self.retention_count]]:
                    should_delete = True
                    reason = "exceeds_retention_count"
            
            if should_delete:
                try:
                    backup_path = Path(backup["path"])
                    backup_path.unlink(missing_ok=True)
                    
                    # Удаление метаданных
                    metadata_path = backup_path.with_suffix(".json")
                    metadata_path.unlink(missing_ok=True)
                    if backup_path.suffix == ".gz":
                        metadata_path = backup_path.with_suffix(".db.json")
                        metadata_path.unlink(missing_ok=True)
                    
                    deleted.append({
                        "filename": backup["filename"],
                        "reason": reason
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to delete backup {backup['filename']}: {e}")
        
        if deleted:
            logger.info(f"🗑️ Cleaned up {len(deleted)} old backups")
        
        return {
            "deleted_count": len(deleted),
            "deleted": deleted
        }
    
    def get_backup_info(self, backup_filename: str) -> Optional[Dict[str, Any]]:
        """Получение информации о конкретном бэкапе"""
        backup_path = self.backup_dir / backup_filename
        
        if not backup_path.exists():
            return None
        
        metadata_path = backup_path.with_suffix(".json")
        if backup_path.suffix == ".gz":
            metadata_path = backup_path.with_suffix(".db.json")
        
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "filename": backup_filename,
            "size": backup_path.stat().st_size,
            "created_at": datetime.fromtimestamp(
                backup_path.stat().st_mtime
            ).isoformat()
        }
    
    def _format_size(self, size_bytes: int) -> str:
        """Форматирование размера файла"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"
    
    async def start_scheduled_backups(self, interval_hours: int = 6):
        """
        Запуск автоматического резервного копирования по расписанию
        
        Args:
            interval_hours: Интервал между бэкапами в часах
        """
        async def backup_loop():
            while True:
                try:
                    await asyncio.sleep(interval_hours * 3600)
                    logger.info("🔄 Running scheduled backup...")
                    result = await self.create_backup(
                        description="Scheduled backup",
                        backup_type="scheduled"
                    )
                    if result["success"]:
                        await self.cleanup_old_backups()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Scheduled backup failed: {e}")
        
        self._scheduler_task = asyncio.create_task(backup_loop())
        logger.info(f"⏰ Scheduled backups started (every {interval_hours} hours)")
    
    def stop_scheduled_backups(self):
        """Остановка автоматического резервного копирования"""
        if self._scheduler_task:
            self._scheduler_task.cancel()
            self._scheduler_task = None
            logger.info("⏰ Scheduled backups stopped")


# Глобальный экземпляр
backup_service = BackupService()
