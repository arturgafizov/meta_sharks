import logging
from smtplib import SMTPRecipientsRefused


def except_shell(errors=(Exception,), default_value=None):
    def decorator(func):
        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except errors as e:
                logging.error(e)
                return default_value
        return new_func
    return decorator


smtp_shell = except_shell((SMTPRecipientsRefused,), default_value=False)
