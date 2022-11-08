from drf_yasg import openapi

tags_auth = ['Auth']
tags_students = ['Students']
tags_excel = ['Excel']

login = {
    'operation_description': '## Авторизация пользователя',
    'operation_summary': 'Авторизация пользователя',
    'tags': tags_auth,
}


signup_schema = {
    'operation_description': '## Апи для регестрации новых пользователей',
    'operation_summary': 'Апи для регестрации новых пользователей',
    'tags': tags_auth,
    'responses': {
        "400": openapi.Response(
            description="Response, when information is invalid.",
            examples={
                "application/json": {
                    "password1": [
                        'password invalid',
                        "The two password fields didn't match",
                    ],
                    'email': [
                        'User is already registered with this e-mail address'
                    ],
                    'username': [
                        'User is already exist with username - new username'
                    ],
                }
            }
        )
    }
}

student_group_create = {
    'operation_description': '## Создание студентов',
    'operation_summary': 'Создание студентов',
    'tags': tags_students,
}

student_group_update = {
    'operation_description': '## Обновление студентов',
    'operation_summary': 'Обновление студентов',
    'tags': tags_students,
}

student_group_partial_update = {
    'operation_description': '## Обновление отдельного поля студентов',
    'operation_summary': 'Частичное обновление студентов',
    'tags': tags_students,
}

student_group_list = {
    'operation_description': '## Получение списка студентов',
    'operation_summary': 'Получение списка студентов',
    'tags': tags_students,
}

student_group_retrieve = {
    'operation_description': '## Получение студентов',
    'operation_summary': 'Получение студентов',
    'tags': tags_students,
}

student_group_destroy = {
    'operation_description': '## Удаление студентов',
    'operation_summary': 'Удаление студентов',
    'tags': tags_students,
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

student_add_in_group = {
    'operation_description': '## Добавление студента в группу',
    'operation_summary': 'Добавление студента в группу',
    'tags': tags_students,
}

generate_excel_file = {
    'operation_description': '## Апи для формирования эксель очета',
    'operation_summary': 'Апи формирует отчет и загружает  в папку  media проекта',
    'tags': tags_excel,
}

get_excel_file = {
    'operation_description': '## Апи для загрузки отчета через таску',
    'operation_summary': 'Апи формирует отчет и загружает в папку  media проекта через селеру таск',
    'tags': tags_excel,
}
