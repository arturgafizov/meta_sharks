from drf_yasg import openapi

tags_groups = ['Students Group']
tags_list_groups = ['Students Group']

student_group_create = {
    'operation_description': '## Создание учебной группы',
    'operation_summary': 'Создание учебной группы',
    'tags': tags_groups,
}

student_group_update = {
    'operation_description': '## Обновление учебной группы',
    'operation_summary': 'Обновление учебной группы',
    'tags': tags_groups,
}

student_group_partial_update = {
    'operation_description': '## Обновление отдельного поля учебной группы',
    'operation_summary': 'Частичное обновление учебной группы',
    'tags': tags_groups,
}

student_group_list = {
    'operation_description': '## Получение списка учебной группы',
    'operation_summary': 'Получение списка учебной группы',
    'tags': tags_list_groups,
}

student_group_retrieve = {
    'operation_description': '## Получение учебной группы',
    'operation_summary': 'Получение учебной группы',
    'tags': tags_groups,
}

student_group_destroy = {
    'operation_description': '## Удаление учебной группы',
    'operation_summary': 'Удаление учебной группы',
    'tags': tags_groups,
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
