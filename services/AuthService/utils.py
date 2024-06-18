from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import logging

# Configura el logger
logger = logging.getLogger(__name__)


def send_token_email(user_email, token):
    subject = 'Recupera tu contraseña'
    message = f'Tu token para recuperar tu contraseña es: {token}'

    template = render_to_string('email.html', {
        'message': message
    })

    email = EmailMessage(
        subject,
        template,
        from_email=settings.EMAIL_HOST_USER,
        to=[user_email]
    )
    email.fail_silently = False

    try:
        email.send()
        return True
    except Exception as e:
        logger.error(f'Error al enviar el correo: {e}')
        return False
