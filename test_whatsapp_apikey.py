import os
from twilio.rest import Client

# Get credentials from environment
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
api_key = os.environ.get('TWILIO_API_KEY')
api_secret = os.environ.get('TWILIO_API_SECRET')
from_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')

print("📱 Testing WhatsApp Integration with API Key...")
print(f"Account SID: {account_sid[:8]}..." if account_sid else "Account SID: Missing")
print(f"API Key: {api_key[:8]}..." if api_key else "API Key: Missing")
print(f"API Secret: {'*' * 8}..." if api_secret else "API Secret: Missing")
print(f"From Number: {from_number}" if from_number else "From Number: Missing")
print()

if not all([account_sid, api_key, api_secret, from_number]):
    print("❌ Missing credentials!")
    exit(1)

try:
    # Initialize Twilio client with API Key authentication
    client = Client(api_key, api_secret, account_sid)
    
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
    import traceback
    traceback.print_exc()
    exit(1)
