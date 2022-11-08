from os import environ
from typing import Union, List
from celery.result import AsyncResult
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.translation import activate

from .decorators import smtp_shell
from source.celery import app

from .excel import ExcelFileOperation
from .services import UsersService
from ..directions.models import Direction
from ..groups.models import StudentGroup


@app.task(name='email.send_information_email')
def send_information_email(
    subject: str,
    template_name: str,
    context: dict,
    to_email: Union[list[str], str],
    letter_language: str = 'en',
    **kwargs,
):
    """
    :param subject: email subject
    :param template_name: template path to email template
    :param context: data what will be passed into email
    :param to_email: receiver email(s)
    :param letter_language: translate letter to selected lang
    :param kwargs: from_email, bcc, cc, reply_to and file_path params
    """
    activate(letter_language)
    to_email: list = [to_email] if isinstance(to_email, str) else to_email
    email_message = EmailMultiAlternatives(
        subject=subject,
        from_email=kwargs.get('from_email'),
        to=to_email,
        bcc=kwargs.get('bcc'),
        cc=kwargs.get('cc'),
        reply_to=kwargs.get('reply_to'),
    )
    html_email: str = loader.render_to_string(template_name, context)
    email_message.attach_alternative(html_email, 'text/html')
    if file_path := kwargs.get('file_path'):
        file_path = environ.get('APP_HOME', environ.get('HOME')) + file_path
        email_message.attach_file(file_path, kwargs.get('mimetype'))
    return send_email(email_message)


@smtp_shell
def send_email(email_message: EmailMultiAlternatives):
    email_message.send()
    return True


@app.task(name='generate_excel_report')
def generate_excel_report():

    titles = [('направление подготовки / куратор', 16000),
              ('название группы /кол-во мужчин /кол-во женщин /кол-во свободных мест. | cтуденты группы', 26000)]
    directions_date = list(Direction.objects.all())
    groups_date = list(StudentGroup.objects.all())
    data = {
        'directions': directions_date,
        'groups_date': groups_date,
    }
    url_file = UsersService.get_file_url_and_file_root('export')

    service = ExcelFileOperation(url_file, titles, data)
    service.xcl_export()
