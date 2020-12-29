from io import BytesIO
from celery import task
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order




# Async creates an email, and a pdf-receipt and send it to the customer
@task
def payment_completed(order_id):
    # This automatically sends an email when a
    # successful order is placed
    order = Order.objects.get(id=order_id)
    # Creates an invoice email
    subject = f'My Shop - EE Invoice no. {order.id}'
    message = 'Please, find attached the invoice for your recent purchase.'
    email = EmailMessage(subject,
                         message,
                         'admin@myshop.com',
                         [order.email])
    # Generate the pdf invoice
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

    # Attach the pdf file
    email.attach(f'order_{order.id}.pdf',
                 out.getvalue(),
                 'application/pdf')

    # Send the email
    email.send()
