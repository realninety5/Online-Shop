#Online Shop

##This project is an online shopping project which incooperates the following

1. Allows users to browse a list of products or category.
2. Using Redis, it stores items that are always bought together. Then recommends them in the product's list and cart page.
3. Uses Celery (with Rabbitmq as *message broker*) to promt an asyn task which promts Weasy-print to produce a pdf invoice and sends a synchronous mail to the buyer.
4. Utilises Django internalization (translation) using django-parler to render the pages in English and Spanish
5. Implements a coupon system to offer discounts to customers.
6. Implements Braintree's payment gateway system to enable customers pay with visa card.
