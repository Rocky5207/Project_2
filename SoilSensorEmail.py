# Project Title: Plant Moisture Sensor with Scheduled Email Notification
# Author: Yuxuan Chen
# Student ID: 202283890031
# Date: 23/4/2025

import RPi.GPIO as GPIO
import smtplib
import time
from datetime import datetime, time as dt_time
from email.message import EmailMessage

# ===== Sensor Configuration =====
SENSOR_PIN = 4  # GPIO4 (BCM numbering)
REPORT_TIMES = [10, 14, 18, 22]  # Hours when reports should be sent (24-hour format)

# ===== Email Configuration (163 example) =====
SMTP_SERVER = 'smtp.163.com'
SMTP_PORT = 25
SENDER_EMAIL = "15961169096@163.com"
SENDER_PASSWORD = "MSTtq32hYp8MiRcz" 
RECEIVER_EMAIL = "642962313@qq.com"

# ===== GPIO Initialization =====
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN)
    print("GPIO initialization completed")

# ===== Beautiful Email Template =====
def create_email_html(status, sensor_value):
    color = "red" if status else "green"
    status_text = "WATER NEEDED!" if status else "Moisture OK"
    
    return f"""
<html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .status {{
                color: {color};
                font-weight: bold;
                font-size: 24px;
                margin: 20px 0;
            }}
            .container {{
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 20px;
                max-width: 500px;
                margin: 0 auto;
            }}
            .footer {{
                margin-top: 20px;
                font-size: 12px;
                color: #777;
            }}
            .sensor-value {{
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🌱 Plant Status Report</h2>
            <div class="status">Status: {status_text}</div>
            <p>Detection time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <div class="sensor-value">
                Sensor reading: <strong>{'DRY' if sensor_value else 'WET'}</strong>
            </div>
            <p>{'⚠️ Your plant needs watering!' if sensor_value else '✅ Your plant has sufficient moisture.'}</p>
            <div class="footer">
                This is an automated message from your Plant Monitoring System.
            </div>
        </div>
    </body>
</html>
"""

# ===== Email Sending Function =====
def send_email(status, test=False):
    try:
        current_status = GPIO.input(SENSOR_PIN)
        subject = f"[Plant Alert] Water needed!" if current_status else "[Plant OK] Status normal"
        
        if test:
            subject = "[TEST] Plant Monitoring System Started"
            message = "The plant monitoring system has started successfully! This is a test email."
            html_content = create_email_html(current_status, current_status)
            html_content = html_content.replace("🌱 Plant Status Report", "🌱 Plant Monitoring System - Test Email")
        else:
            message = "Water needed!" if current_status else "Moisture sufficient"
            html_content = create_email_html(current_status, current_status)  # Fixed this line

        msg = EmailMessage()
        msg.set_content(message)
        msg.add_alternative(html_content, subtype='html')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"Email sent successfully at {datetime.now().strftime('%H:%M:%S')}")
        return True

    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False

# ===== Check if it's time to send report =====
def should_send_report():
    now = datetime.now()
    return now.hour in REPORT_TIMES and now.minute == 0

# ===== Main Program =====
if __name__ == "__main__":
    try:
        setup_gpio()
        
        # Send test email immediately
        print("Sending test email...")
        send_email(False, test=True)
        
        print("Plant monitoring system started. Waiting for report times...")
        print(f"Reports will be sent at: {', '.join(str(t)+':00' for t in REPORT_TIMES)}")
        
        last_sent_hour = -1  # Track last sent hour to avoid duplicate sends
        
        while True:
            now = datetime.now()
            
            # Check if it's time to send a report
            if now.hour in REPORT_TIMES and now.minute == 0 and now.hour != last_sent_hour:
                current_status = GPIO.input(SENSOR_PIN)
                print(f"Sending scheduled report at {now.hour}:00...")
                if send_email(current_status):
                    last_sent_hour = now.hour
                else:
                    # Retry if failed
                    time.sleep(60)
                    continue
            
            # Sleep for 50 seconds to check again (just after the minute changes)
            time.sleep(50)
            
    except KeyboardInterrupt:
        print("\nProgram terminated")
    finally:
        GPIO.cleanup()
