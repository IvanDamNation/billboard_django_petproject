from datetime import datetime
from os.path import splitext

from django.core.signing import Signer
from django.template.loader import render_to_string

from billboard_idn_prj.settings import ALLOWED_HOSTS, env

signer = Signer()


def send_activation_notification(user):
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0] + ':' + env.str("PORT")
    else:
        host = 'http://127.0.0.1' + ':' + env.str("PORT")
    context = {
        'user': user,
        'host': host,
        'sign': signer.sign(user.username)
    }
    subject = render_to_string('email/activation_letter_subject.txt', context)
    body_text = render_to_string('email/activation_letter_body.txt', context)
    user.email_user(subject, body_text)


def get_timestamp_path(instance, filename):
    return f"{datetime.now().timestamp()}{splitext(filename)[1]}"
