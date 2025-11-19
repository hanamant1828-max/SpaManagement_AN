import os
from twilio.rest import Client

# Get credentials from environment
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
from_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')

print("📱 Testing WhatsApp Integration...")
print(f"Account SID: {account_sid[:8]}..." if account_sid else "Account SID: Missing")
print(f"Auth Token: {'*' * 8}..." if auth_token else "Auth Token: Missing")
print(f"From Number: {from_number}" if from_number else "From Number: Missing")
print()

if not all([account_sid, auth_token, from_number]):
    print("❌ Missing credentials!")
    exit(1)

try:
    # Initialize Twilio client
    client = Client(account_sid, auth_token)
    
    # Format phone number for WhatsApp
    to_number = '+917022478751'
    if not to_number.startswith('whatsapp:'):
        to_number = f'whatsapp:{to_number}'
    
    # Send test message
    message = client.messages.create(
        from_=from_number,
        body='🎉 Hello! This is a test message from your Spa & Salon Suite management system. WhatsApp integration is working perfectly!',
        to=to_number
    )
    
    print(f"✅ WhatsApp message sent successfully!")
    print(f"Message SID: {message.sid}")
    print(f"Status: {message.status}")
    print(f"To: {to_number}")
    print(f"From: {from_number}")
    print()
    print("🎊 WhatsApp integration test completed successfully!")
    
except Exception as e:
    print(f"❌ Error sending WhatsApp message: {e}")
    exit(1)
