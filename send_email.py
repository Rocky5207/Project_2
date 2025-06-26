import smtplib
from email.message import EmailMessage

# NetEase 163 Email Settings
email_user = "17834623809@163.com"  # Your full email
email_pass = "BMgynVuZcyCghEym"     # Your password
recipient = "2627932466@qq.com"      # Recipient email

# Create the email
msg = EmailMessage()
msg.set_content("Hello from Raspberry Pi via NetEase 163!")
msg["Subject"] = "Test Email from 163"
msg["From"] = email_user
msg["To"] = recipient

try:
    # Method 1: SSL (Port 465)
    with smtplib.SMTP_SSL("smtp.163.com", 465) as server:
        server.login(email_user, email_pass)
        server.send_message(msg)
    print("✅ Email sent successfully (SSL)!")
    
    # Alternative: STARTTLS (Port 587)
    # with smtplib.SMTP("smtp.163.com", 587) as server:
    #     server.starttls()
    #     server.login(email_user, email_pass)
    #     server.send_message(msg)
    # print("✅ Email sent successfully (STARTTLS)!")
    
except Exception as e:
    print(f"❌ Error: {e}")
