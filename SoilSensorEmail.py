# Project Title: Plant Moisture Sensor with Scheduled Email Notification
# Author: Xu Junjie
# Student ID: 202383890027
# Date: 26/6/2025

import RPi.GPIO as GPIO
import smtplib
import time
from datetime import datetime, time as dt_time
from email.message import EmailMessage

# ===== Sensor Configuration =====
SENSOR_PIN = 4  # GPIO4 (BCM numbering)
REPORT_TIMES = [8, 12, 16, 20]  # Hours when reports should be sent (24-hour format)

# ===== Email Configuration (163 example) =====
SMTP_SERVER = 'smtp.163.com'
SMTP_PORT = 25
SENDER_EMAIL = "17834623809@163.com"
SENDER_PASSWORD = "BMgynVuZcyCghEym" 
RECEIVER_EMAIL = "2627932466@qq.com"

# ===== GPIO Initialization =====
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN)
    print("GPIO initialization completed")

# ===== Beautiful Email Template =====
def create_email_html(status, sensor_value):
    alert_color = "#e74c3c" if status else "#2ecc71"
    alert_text = "Urgent: Water Required!" if status else "Soil Moisture Level: Normal"
    moisture_label = "Dry" if sensor_value else "Moist"
    advice = "Watering is advised." if sensor_value else "No action is needed."

    return f"""
<html>
<head>
<style>
body {{
    font-family: 'Segoe UI', sans-serif;
    background-color: #f9f9f9;
    color: #333;
}}
.report-card {{
    background-color: #ffffff;
    border-left: 6px solid {alert_color};
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    padding: 24px;
    border-radius: 10px;
    width: 90%;
    max-width: 540px;
    margin: 30px auto;
}}
.status-header {{
    font-size: 22px;
    font-weight: 600;
    color: {alert_color};
    margin-bottom: 12px;
}}
.timestamp {{
    font-size: 14px;
    color: #999;
    margin-bottom: 10px;
}}
.sensor-data {{
    font-family: monospace;
    font-size: 16px;
    padding: 10px;
    background-color: #eef3f7;
    border-radius: 6px;
    margin: 12px 0;
}}
.note {{
    font-size: 14px;
    margin-top: 10px;
}}
.footer {{
    font-size: 12px;
    text-align: center;
    color: #aaa;
    margin-top: 20px;
}}
</style>
</head>
<body>
<div class="report-card">
    <div class="status-header">{alert_text}</div>
    <div class="timestamp">Time Checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    <div class="sensor-data">Soil Condition: <strong>{moisture_label}</strong></div>
    <div class="note">{advice}</div>
    <div class="footer">
        Message sent from your Smart Garden System.
    </div>
</div>
</body>
</html>
"""

# ===== Email Sending Function =====
def send_email(status, test=False):
    try:
        current_status = GPIO.input(SENSOR_PIN)
        subject = f"[Plant Alert] Water needed!!!" if current_status else "[Plant is OK] Status normal"
        
        if test:
            subject = "[TEST] Plant Monitoring System Started"
            message = "The plant monitoring system has started successfully! This is a test email."
            html_content = create_email_html(current_status, current_status)
            html_content = html_content.replace("Plant Status Report", "Plant Monitoring System - Test Email")
        else:
            message = "Water needed!!!" if current_status else "Adequate Moisture"
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
