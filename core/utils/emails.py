from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_welcome_email(user):
    subject = "Welcome to Expa Logistics 🚚"
    html_message = render_to_string("accounts/welcome_email.html", {"user": user})
    plain_message = strip_tags(html_message)
    from_email = None
    to = [user.email]

    send_mail(subject, plain_message, from_email, to, html_message=html_message)




def send_order_creation_email(user, order):
    subject = f"Order #{order.package_id} Created Successfully"
    html_message = render_to_string("deliveries/package_creation_email.html", {"user": user, "order": order})
    plain_message = strip_tags(html_message)
    from_email = None
    to = [user.email]


    send_mail(subject, plain_message, from_email, to, html_message=html_message)




def send_order_creation_email_admin(user, order):
    subject = f"Order #{order.package_id} Created Successfully"
    html_message = render_to_string("deliveries/admin_package_creation_email.html", {"user": user, "order": order})
    plain_message = strip_tags(html_message)
    from_email = None
    to = ['app.orders@expa.co.ke']


    send_mail(subject, plain_message, from_email, to, html_message=html_message)




