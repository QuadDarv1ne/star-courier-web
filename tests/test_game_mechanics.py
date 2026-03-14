"""
Тесты для системы игровых механик (главы 11-18)
"""

import sys
sys.path.insert(0, 'backend')

from app.services.game_mechanics_service import (
    get_game_mechanics_manager,
    reset_game_mechanics_manager,
    PathType,
    EndingType
)


def test_initialization():
    """Тест 1: Инициализация"""
    reset_game_mechanics_manager()
    m = get_game_mechanics_manager()
    state = m.get_player_state()
    
    assert state['resonance']['level'] == 1
    assert state['mental_state']['health'] == 100
    assert state['mental_state']['influence'] == 0
    assert state['path']['type'] is None
    assert 'exile' in state['endings']['available']
    print('✓ Test 1: Инициализация')


def test_resonance_level_up():
    """Тест 2: Повышение уровня Резонанса"""
    reset_game_mechanics_manager()
    m = get_game_mechanics_manager()
    
    result = m.gain_resonance_exp(150)
    assert result['level_up'] == True
    assert m.resonance.level == 2
    assert result['bonus']['anomaly_detection_radius'] == 500
    print('✓ Test 2: Резонанс level up')


def test_path_choice():
    """Тест 3: Выбор пути"""
    reset_game_mechanics_manager()
    m = get_game_mechanics_manager()
    
    result = m.choose_path('observer')
    assert result['path'] == 'observer'
    assert result['bonus']['psychic_boost'] == 20
    
    result = m.choose_path('alliance')
    assert result['path'] == 'alliance'
    assert result['bonus']['credits'] == 5000
    
    result = m.choose_path('independence')
    assert result['path'] == 'independence'
    assert result['bonus']['network_access'] == True
    print('✓ Test 3: Выбор пути')


def test_mental_state():
    """Тест 4: Ментальное состояние"""
    reset_game_mechanics_manager()
    m = get_game_mechanics_manager()
    
    # influence_change=10 уменьшает health на 10//2=5
    result = m.update_mental_state(-15, 10)
    assert result['health'] == 80  # 100 - 15 - 5
    assert result['influence'] == 10
    assert result['state'] == 'normal'
    
    result = m.update_mental_state(-25, 0)
    assert result['health'] == 55
    assert result['state'] == 'visions'
    print('✓ Test 4: Ментальное состояние')


def test_entity_contact():
    """Тест 5: Контакт с Сущностью"""
    reset_game_mechanics_manager()
    m = get_game_mechanics_manager()
    m.player_stats['psychic'] = 50
    
    result = m.entity_contact(30)
    # psychic_protection = 50 // 10 = 5
    # influence_gain = 30 - 5 = 25
    # health_loss = 30 // 2 = 15 (от change_health)
    # health_loss += 25 // 2 = 12 (от change_influence)
    # total health_loss = 27
    assert result['influence'] == 25
    assert result['health'] == 73  # 100 - 27
    print('✓ Test 5: Контакт с Сущностью')


def test_ending_unlock():
    """Тест 6: Разблокировка финала"""
    reset_game_mechanics_manager()
    m = get_game_mechanics_manager()
    
    # Exile доступен всегда
    assert 'exile' in [e.value for e in m.ending_system.available_endings]
    
    # Treaty разблокируется при progress >= 50
    # Первый выбор с path удваивает прогресс: 25 * 2 = 50
    m.make_path_choice({'path': 'alliance', 'progress': 25, 'choice_id': 'test'})
    
    endings = [e.value for e in m.ending_system.available_endings]
    assert 'treaty' in endings
    print('✓ Test 6: Разблокировка финала')


def test_ending_requirements():
    """Тест 7: Требования к финалам"""
    reset_game_mechanics_manager()
    m = get_game_mechanics_manager()
    
    # Exile доступен всегда
    result = m.check_ending_availability('exile')
    assert result['available'] == True
    
    # Treaty требует Psychic 70+
    m.player_stats['psychic'] = 50
    result = m.check_ending_availability('treaty')
    assert result['requirements_met'] == False
    
    m.player_stats['psychic'] = 70
    result = m.check_ending_availability('treaty')
    assert result['requirements_met'] == True
    
    # Merge требует Psychic 90+ и Resonance 4
    m.player_stats['psychic'] = 90
    m.player_stats['resonance_level'] = 3
    result = m.check_ending_availability('merge')
    assert result['requirements_met'] == False
    
    m.resonance.level = 4
    m.player_stats['resonance_level'] = 4
    result = m.check_ending_availability('merge')
    assert result['requirements_met'] == True
    print('✓ Test 7: Требования к финалам')


def test_path_progress():
    """Тест 8: Прогресс пути"""
    reset_game_mechanics_manager()
    m = get_game_mechanics_manager()
    
    # Первый выбор удваивает прогресс
    result = m.make_path_choice({'path': 'observer', 'progress': 20, 'choice_id': 'c1'})
    assert result['progress'] == 40  # 20 * 2
    assert result['choices_made'] == 1
    
    result = m.make_path_choice({'path': 'observer', 'progress': 10, 'choice_id': 'c2'})
    assert result['progress'] == 50  # 40 + 10
    assert result['choices_made'] == 2
    print('✓ Test 8: Прогресс пути')


if __name__ == '__main__':
    test_initialization()
    test_resonance_level_up()
    test_path_choice()
    test_mental_state()
    test_entity_contact()
    test_ending_unlock()
    test_ending_requirements()
    test_path_progress()
    print('\n✅ Все тесты пройдены!')
