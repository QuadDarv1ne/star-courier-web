import json

# Проверка сцен из архива
scenes = json.load(open('scenes_ch11_18.json', encoding='utf-8'))
scene_list = list(scenes.get('scenes', {}).keys())
print(f'Сцены в архиве: {len(scene_list)}')
for s in scene_list:
    scene = scenes['scenes'][s]
    ch = scene.get('chapter', '?')
    print(f'  Глава {ch}: {s}')
