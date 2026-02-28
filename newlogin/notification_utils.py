"""
Email/SMS helpers: registration credentials and OTP notifications.
"""
import logging
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_registration_email(email, username, password, name=None):
    """Send username and password to the user's email. Returns (success: bool, error_message: str|None)."""
    subject = 'Your registration credentials'
    name_part = f'Hi {name},\n\n' if name else ''
    body = (
        f'{name_part}'
        f'Your account has been created.\n\n'
        f'Username (mobile number): {username}\n'
        f'Password: {password}\n\n'
        f'Use these to login. You can change your password using the forgot-password option.\n\n'
        f'Do not share this email with anyone.'
    )
    from_email = settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=[email],
            fail_silently=False,
        )
        return True, None
    except Exception as e:
        err_msg = str(e)
        logger.exception('Failed to send registration email to %s: %s', email, e)
        return False, err_msg


def send_registration_sms(phone, username, password):
    """Send username and password via SMS. Uses SMS_GATEWAY_URL if set."""
    message = (
        f'Your login: Username {username}, Password {password}. '
        f'Use these to login. Keep this secure.'
    )
    url_template = getattr(settings, 'SMS_GATEWAY_URL', '') or ''
    if not url_template:
        logger.info('SMS not configured. Would send to %s: %s', phone, message)
        return True
    try:
        encoded_msg = urllib.parse.quote(message)
        url = url_template.format(phone=phone, message=encoded_msg)
        req = urllib.request.Request(url, method=getattr(settings, 'SMS_GATEWAY_METHOD', 'GET'))
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 201):
                return True
            logger.warning('SMS gateway returned status %s', resp.status)
            return False
    except Exception as e:
        logger.exception('Failed to send registration SMS to %s: %s', phone, e)
        return False


def send_otp_email(email: str, code: str) -> bool:
    """Send a one-time password (OTP) to the given email. Returns True on success."""
    if not email:
        return False
    subject = 'Your one-time password (OTP)'
    body = (
        f'Your OTP is: {code}\n\n'
        f'This code is valid for a short time. '
        f'Do not share this code with anyone.'
    )
    from_email = settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.exception('Failed to send OTP email to %s: %s', email, e)
        return False


def send_otp_sms(phone: str, code: str) -> bool:
    """Send a one-time password (OTP) via SMS. Uses SMS_GATEWAY_URL if set."""
    if not phone:
        return False
    message = (
        f'Your OTP is {code}. '
        f'Do not share this code with anyone.'
    )
    url_template = getattr(settings, 'SMS_GATEWAY_URL', '') or ''
    if not url_template:
        logger.info('SMS not configured. Would send OTP to %s: %s', phone, message)
        return True
    try:
        encoded_msg = urllib.parse.quote(message)
        url = url_template.format(phone=phone, message=encoded_msg)
        req = urllib.request.Request(url, method=getattr(settings, 'SMS_GATEWAY_METHOD', 'GET'))
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 201):
                return True
            logger.warning('SMS gateway returned status %s', resp.status)
            return False
    except Exception as e:
        logger.exception('Failed to send OTP SMS to %s: %s', phone, e)
        return False
