from drf_yasg import openapi

tags_direction = ['Direction']
tags_subject = ['Subject']


add_curator_direction = {
    'operation_description': '## Апи для добавление куратора к направлению подготовки',
    'operation_summary': 'Апи для добавление куратора к направлению подготовки',
    'tags': tags_direction,
}

direction_create = {
    'operation_description': '## Создание направления подготовки',
    'operation_summary': 'Создание направления подготовки',
    'tags': tags_direction,
}

direction_update = {
    'operation_description': '## Обновление направления подготовки',
    'operation_summary': 'Обновление направления подготовки',
    'tags': tags_direction,
}

direction_partial_update = {
    'operation_description': '## Обновление отдельного поля направления подготовки',
    'operation_summary': 'Частичное обновление направления подготовки',
    'tags': tags_direction,
}

direction_list = {
    'operation_description': '## Получение списка направления подготовки',
    'operation_summary': 'Получение списка направления подготовки',
    'tags': tags_direction,
}

direction_retrieve = {
    'operation_description': '## Получение направления подготовки',
    'operation_summary': 'Получение направления подготовки',
    'tags': tags_direction,
}

direction_destroy = {
    'operation_description': '## Удаление направления подготовки',
    'operation_summary': 'Удаление направления подготовки',
    'tags': tags_direction,
    'responses': {
        '204': openapi.Response(
            description='Response, when obj deleted.',
            examples={
                'application/json': {
                    'detail': '204 no content',
                }
            }
        )
    }
}

subject_create = {
    'operation_description': '## Создание учебной дисциплины',
    'operation_summary': 'Создание учебной дисциплины',
    'tags': tags_subject,
}

subject_update = {
    'operation_description': '## Обновление учебной дисциплины',
    'operation_summary': 'Обновление учебной дисциплины',
    'tags': tags_subject,
}

subject_partial_update = {
    'operation_description': '## Обновление отдельного поля учебной дисциплины',
    'operation_summary': 'Частичное обновление учебной дисциплины',
    'tags': tags_subject,
}

subject_list = {
    'operation_description': '## Получение списка учебных дисциплин',
    'operation_summary': 'Получение списка учебных дисциплин',
    'tags': tags_subject,
}

subject_retrieve = {
    'operation_description': '## Получение учебной дисциплины',
    'operation_summary': 'Получение учебной дисциплины',
    'tags': tags_subject,
}

subject_destroy = {
    'operation_description': '## Удаление учебной дисциплины',
    'operation_summary': 'Удаление учебной дисциплины',
    'tags': tags_subject,
    'responses': {
        '204': openapi.Response(
            description='Response, when obj deleted.',
            examples={
                'application/json': {
                    'detail': '204 no content',
                }
            }
        )
    }
}
