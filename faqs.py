#!/usr/bin/python3

from entry import app, db
from entry.models import FAQ

faq_data = [
    {
        'question': 'What is your return policy?',
        'answer': 'Our return policy allows for returns up to 30 days after purchase. Items must be in new, unused condition and in their original packaging.'
    },
    {
        'question': 'How can I track my order?',
        'answer': 'Once your order has been shipped, you will receive a tracking number via email. You can use this tracking number to monitor the status of your shipment.'
    },
    {
        'question': 'Do you offer international shipping?',
        'answer': 'Yes, we offer international shipping to most countries. Shipping costs and delivery times may vary depending on the destination.'
    },
    {
        'question': 'What payment methods do you accept?',
        'answer': 'We accept Visa, Mastercard, American Express, and PayPal.'
    },
    {
        'question': 'How can I contact customer support?',
        'answer': 'You can contact our customer support team via email at support@example.com or by phone at 1-800-123-4567.'
    },
    {
        'question': 'How do I schedule a parcel pickup?',
        'answer': 'You can schedule a parcel pickup by logging into your account on our website and selecting the "Schedule Pickup" option.'
    },
    {
        'question': 'What are your pickup and delivery hours?',
        'answer': 'Our pickup and delivery hours are from 9:00 AM to 6:00 PM, Monday through Friday.'
    },
    {
        'question': 'Do you provide packaging materials?',
        'answer': 'Yes, we offer packaging materials such as boxes, tape, and bubble wrap for purchase.'
    },
    {
        'question': 'Can I request a specific delivery time?',
        'answer': 'While we cannot guarantee specific delivery times, you can provide delivery instructions during checkout, and we will do our best to accommodate your request.'
    },
    {
        'question': 'How can I change my delivery address?',
        'answer': 'You can update your delivery address by logging into your account and editing your profile information.'
    },
    {
        'question': 'Do you offer same-day delivery?',
        'answer': 'Yes, we offer same-day delivery for orders placed before 12:00 PM local time. Additional charges may apply.'
    },
    {
        'question': 'What happens if my parcel is lost or damaged during transit?',
        'answer': 'In the rare event that your parcel is lost or damaged during transit, please contact our customer support team immediately for assistance.'
    },
    {
        'question': 'Can I track my parcel in real-time?',
        'answer': 'Yes, you can track your parcel in real-time using the tracking number provided in your order confirmation email.'
    },
    {
        'question': 'How do I cancel my pickup request?',
        'answer': 'To cancel a pickup request, please contact our customer support team at least 24 hours before the scheduled pickup time.'
    },
    {
        'question': 'Are there any restrictions on the size or weight of parcels?',
        'answer': 'Yes, parcels must not exceed a certain weight and size limit. Please refer to our website for specific guidelines.'
    },
    {
        'question': 'Do you offer insurance for parcels?',
        'answer': 'Yes, we offer insurance options for parcels to provide additional protection against loss or damage.'
    },
    {
        'question': 'How can I become a registered user?',
        'answer': 'You can sign up for a user account on our website by providing your contact information and creating a password.'
    },
    {
        'question': 'Are there any discounts for frequent shippers?',
        'answer': 'Yes, we offer discounts and rewards programs for frequent shippers. Please contact our customer support team for more information.'
    },
    {
        'question': 'What forms of identification are required for parcel pickup?',
        'answer': 'You may be required to present a valid photo ID, such as a driver\'s license or passport, when picking up parcels.'
    },
    {
        'question': 'Can I authorize someone else to pick up my parcel on my behalf?',
        'answer': 'Yes, you can authorize someone else to pick up your parcel by providing them with a copy of your ID and an authorization letter.'
    },
    {
        'question': 'Do you offer special handling for fragile items?',
        'answer': 'Yes, we offer special handling and packaging options for fragile items to ensure they arrive safely at their destination.'
    },
    {
        'question': 'Is there a limit on the number of parcels I can send at once?',
        'answer': 'There may be limits on the number of parcels you can send at once, depending on the size and weight of the parcels.'
    },
    {
        'question': 'How can I pay for my shipping fees?',
        'answer': 'You can pay for your shipping fees online using a credit card or PayPal.'
    },
    {
        'question': 'What safety measures are in place for contactless delivery?',
        'answer': 'Our delivery drivers adhere to strict safety protocols for contactless delivery, including wearing masks and gloves and maintaining social distancing.'
    },
    {
        'question': 'Do you offer parcel storage services?',
        'answer': 'Yes, we offer parcel storage services for customers who need to temporarily store their parcels before delivery.'
    }
]

# Insert FAQ data into the database
with app.app_context():
    for item in faq_data:
        question = item['question']
        answer = item['answer']
        faq = FAQ(question=question, answer=answer)
        db.session.add(faq)

    # Commit the changes
    db.session.commit()

