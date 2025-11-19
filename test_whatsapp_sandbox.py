import os
from twilio.rest import Client

# Get credentials from environment
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

# Use Twilio WhatsApp Sandbox number (standard testing number)
from_number = 'whatsapp:+14155238886'  # Twilio Sandbox
to_number = 'whatsapp:+917022478751'

print("📱 Testing WhatsApp Integration with Sandbox...")
print(f"Account SID: {account_sid[:8]}..." if account_sid else "Account SID: Missing")
print(f"Auth Token: {'*' * 8}..." if auth_token else "Auth Token: Missing")
print(f"From Number (Sandbox): {from_number}")
print(f"To Number: {to_number}")
print()

if not all([account_sid, auth_token]):
    print("❌ Missing credentials!")
    exit(1)

try:
    # Initialize Twilio client
    client = Client(account_sid, auth_token)
    
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
    print()
    print("📱 Please check your WhatsApp for the test message!")
    
except Exception as e:
    print(f"❌ Error sending WhatsApp message: {e}")
    print()
    print("💡 If you're using Twilio Sandbox:")
    print("   1. Open WhatsApp on your phone")
    print("   2. Send a message to +1 415 523 8886")
    print("   3. Use the join code from your Twilio Console")
    print("   4. After joining, try sending the test message again")
    exit(1)
