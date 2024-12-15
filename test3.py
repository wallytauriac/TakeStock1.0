import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Replace these with your credentials and the recipient's email
sender_email = "wallytauriac@comcast.net"
receiver_email = "wallytauriac@gmail.com"
password = ""

# Create the message
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = "Checking the email process"
body = "Hello. How are you? I hope you are doing well."

msg.attach(MIMEText(body, 'plain'))

# Set up the server
server = smtplib.SMTP('smtp.comcast.net', 587)  # Replace 'smtp.example.com' with your email provider's SMTP server
server.starttls()

# Login to the server
server.login(sender_email, password)

# Send the email
text = msg.as_string()
server.sendmail(sender_email, receiver_email, text)

# Quit the server
server.quit()

print("Email sent successfully.")


if __name__ == '__main__':
    print("bye")
