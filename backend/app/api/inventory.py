"""
API для управления инвентарём и крафтом
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.services.inventory_service import (
    InventoryManager, Item, ItemCategory, ItemRarity, InventoryItem
)
from app.services.crafting_service import (
    CraftingManager, CraftingRecipe, CraftingSkill, CraftingResult
)
from app.models.base import APIResponse, ResponseBuilder, ErrorCodeEnum

logger = logging.getLogger('api.inventory')

router = APIRouter()


# ============================================================================
# DEPENDENCIES
# ============================================================================

def get_inventory_manager() -> InventoryManager:
    """Получить менеджер инвентаря"""
    # В реальной реализации - загрузка из БД
    return InventoryManager()


def get_crafting_manager() -> CraftingManager:
    """Получить менеджер крафта"""
    # В реальной реализации - загрузка из БД
    crafting = CraftingManager()
    for recipe in CraftingManager.create_starter_recipes():
        crafting.add_recipe(recipe)
    return crafting


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ItemAddRequest(BaseModel):
    """Запрос на добавление предмета"""
    item_id: str = Field(..., description="ID предмета")
    quantity: int = Field(1, description="Количество", ge=1, le=999)


class ItemRemoveRequest(BaseModel):
    """Запрос на удаление предмета"""
    item_id: str = Field(..., description="ID предмета")
    quantity: int = Field(1, description="Количество", ge=1)


class ItemEquipRequest(BaseModel):
    """Запрос на экипировку предмета"""
    item_id: str = Field(..., description="ID предмета")


class CraftRequest(BaseModel):
    """Запрос на крафт"""
    recipe_id: str = Field(..., description="ID рецепта")


class InventoryFilter(BaseModel):
    """Фильтр инвентаря"""
    category: Optional[ItemCategory] = Field(None, description="Категория")
    rarity: Optional[ItemRarity] = Field(None, description="Редкость")


# ============================================================================
# INVENTORY ENDPOINTS
# ============================================================================

@router.get("/inventory", tags=["🎒 Инвентарь"])
async def get_inventory(
    inventory: InventoryManager = Depends(get_inventory_manager)
):
    """
    Получить весь инвентарь игрока.
    
    Включает:
    - Список предметов
    - Экипировку
    - Статистику
    """
    try:
        items = inventory.list_items()
        stats = inventory.get_stats()
        bonuses = inventory.get_equipped_bonuses()
        
        return APIResponse(
            status="success",
            message="Инвентарь получен",
            data={
                "items": [item.model_dump() for item in items],
                "equipped": {k: v.model_dump() for k, v in inventory.equipped.items()},
                "stats": stats.model_dump(),
                "bonuses": bonuses,
                "max_weight": inventory.max_weight,
                "max_slots": inventory.max_slots
            }
        )
    except Exception as e:
        logger.error(f"Ошибка получения инвентаря: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inventory/add", tags=["🎒 Инвентарь"])
async def add_item(
    request: ItemAddRequest,
    inventory: InventoryManager = Depends(get_inventory_manager)
):
    """
    Добавить предмет в инвентарь.
    
    Предметы можно получать за:
    - Выполнение квестов
    - Победу в бою
    - Крафт
    - Покупку
    """
    try:
        # В реальной реализации - загрузка предмета из БД
        item = Item(
            id=request.item_id,
            name=f"Item {request.item_id}",
            description="Описание предмета",
            category=ItemCategory.MATERIAL,
            rarity=ItemRarity.COMMON,
            value=10,
            weight=0.5
        )
        
        success, message = inventory.add_item(item, request.quantity)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return APIResponse(
            status="success",
            message=message,
            data={"quantity": request.quantity}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка добавления предмета: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inventory/remove", tags=["🎒 Инвентарь"])
async def remove_item(
    request: ItemRemoveRequest,
    inventory: InventoryManager = Depends(get_inventory_manager)
):
    """
    Удалить предмет из инвентаря.
    
    Предметы можно:
    - Продавать
    - Использовать
    - Выбрасывать
    """
    try:
        success, message = inventory.remove_item(request.item_id, request.quantity)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return APIResponse(
            status="success",
            message=message,
            data={}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления предмета: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inventory/equip", tags=["🎒 Инвентарь"])
async def equip_item(
    request: ItemEquipRequest,
    inventory: InventoryManager = Depends(get_inventory_manager)
):
    """
    Экипировать предмет.
    
    Экипировка даёт бонусы к характеристикам.
    Можно экипировать только один предмет в слот.
    """
    try:
        success, message = inventory.equip_item(request.item_id)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        bonuses = inventory.get_equipped_bonuses()
        
        return APIResponse(
            status="success",
            message=message,
            data={"bonuses": bonuses}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка экипировки: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inventory/unequip", tags=["🎒 Инвентарь"])
async def unequip_item(
    request: ItemEquipRequest,
    inventory: InventoryManager = Depends(get_inventory_manager)
):
    """
    Снять предмет.
    
    Снятие предмета убирает его бонусы.
    """
    try:
        success, message = inventory.unequip_item(request.item_id)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return APIResponse(
            status="success",
            message=message,
            data={}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка снятия предмета: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory/stats", tags=["🎒 Инвентарь"])
async def get_inventory_stats(
    inventory: InventoryManager = Depends(get_inventory_manager)
):
    """
    Получить статистику инвентаря.
    
    Включает:
    - Общее количество предметов
    - Общий вес
    - Общая стоимость
    - Распределение по категориям
    """
    try:
        stats = inventory.get_stats()
        
        return APIResponse(
            status="success",
            message="Статистика получена",
            data=stats.model_dump()
        )
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CRAFTING ENDPOINTS
# ============================================================================

@router.get("/crafting/recipes", tags=["🔨 Крафт"])
async def get_recipes(
    crafting: CraftingManager = Depends(get_crafting_manager)
):
    """
    Получить все доступные рецепты.
    
    Фильтруются по уровню навыка игрока.
    """
    try:
        recipes = crafting.get_available_recipes({'psychic': 0})
        
        return APIResponse(
            status="success",
            message="Рецепты получены",
            data={
                "recipes": [recipe.model_dump() for recipe in recipes],
                "total": len(recipes)
            }
        )
    except Exception as e:
        logger.error(f"Ошибка получения рецептов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crafting/recipes/{recipe_id}", tags=["🔨 Крафт"])
async def get_recipe(
    recipe_id: str,
    crafting: CraftingManager = Depends(get_crafting_manager)
):
    """
    Получить详细信息 рецепта.
    """
    try:
        recipe = crafting.get_recipe(recipe_id)
        
        if not recipe:
            raise HTTPException(status_code=404, detail="Рецепт не найден")
        
        return APIResponse(
            status="success",
            message="Рецепт получен",
            data=recipe.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения рецепта: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crafting/craft", tags=["🔨 Крафт"])
async def craft_item(
    request: CraftRequest,
    crafting: CraftingManager = Depends(get_crafting_manager)
):
    """
    Выполнить крафт.
    
    Требования:
    - Достаточный уровень навыка
    - Наличие материалов
    - Успешная проверка шанса
    
    Результаты:
    - Success: получение предмета
    - Critical Success: x2 предмета
    - Failure: потеря материалов
    - Critical Failure: потеря материалов + негативный эффект
    """
    try:
        recipe = crafting.get_recipe(request.recipe_id)
        
        if not recipe:
            raise HTTPException(status_code=404, detail="Рецепт не найден")
        
        # В реальной реализации - загрузка материалов из инвентаря
        available_items = {
            material.item_id: material.quantity * 10
            for material in recipe.materials
        }
        
        player_stats = {'psychic': 30}
        
        result, message, data = crafting.craft(
            recipe,
            available_items,
            player_stats
        )
        
        return APIResponse(
            status="success",
            message=message,
            data=data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка крафта: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crafting/stats", tags=["🔨 Крафт"])
async def get_crafting_stats(
    crafting: CraftingManager = Depends(get_crafting_manager)
):
    """
    Получить статистику крафта.
    
    Включает:
    - Уровни навыков
    - Опыт навыков
    - Статистику успехов
    """
    try:
        stats = {
            "skill_levels": crafting.skill_levels,
            "skill_exp": crafting.skill_exp,
            "stats": {
                skill.value: stat.model_dump()
                for skill, stat in crafting.stats.items()
            }
        }
        
        return APIResponse(
            status="success",
            message="Статистика крафта получена",
            data=stats
        )
    except Exception as e:
        logger.error(f"Ошибка получения статистики крафта: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EXPORT
# ============================================================================


__all__ = ["router"]
