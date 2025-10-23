from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

class EmailService:
    @staticmethod
    def send_template_email(user, template_context, subject, template_name='email_template'):
        """
        Send email using template with context
        """
        html_content = render_to_string(f'emails/{template_name}.html', template_context)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send()
        
    @classmethod
    def send_password_reset_email(cls, info):
        context = {
            'email': info['user'].email,
            'code': info['reset_code'].code
        }
        cls.send_template_email(info['user'], context, info['subject'], template_name='password_reset')