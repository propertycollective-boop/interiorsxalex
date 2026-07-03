import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)


@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json(silent=True) or {}

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    project_type = data.get('project-type', '').strip()
    location = data.get('location', '').strip()
    timeline = data.get('timeline', '').strip()
    message = data.get('message', '').strip()

    if not name or not email:
        return jsonify({'error': 'Name and email are required.'}), 400

    smtp_user = os.environ.get('GMAIL_USER')
    smtp_pass = os.environ.get('GMAIL_APP_PASSWORD')
    to_email = os.environ.get('CONTACT_EMAIL', 'interiorsxalex@gmail.com')

    if not smtp_user or not smtp_pass:
        print('GMAIL_USER or GMAIL_APP_PASSWORD not set')
        return jsonify({'error': 'Server email not configured.'}), 500

    body = f"""New contact form submission — Interiors x Alex

Name:         {name}
Email:        {email}
Phone:        {phone or 'Not provided'}
Project Type: {project_type or 'Not specified'}
Location:     {location or 'Not provided'}
Timeline:     {timeline or 'Not specified'}

Message:
{message or 'No message provided'}
"""

    msg = MIMEMultipart()
    msg['Subject'] = f'New Inquiry from {name} — Interiors x Alex'
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Reply-To'] = email
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
    except Exception as e:
        print(f'Email send error: {e}')
        return jsonify({'error': 'Failed to send message. Please try again.'}), 500

    return jsonify({'success': True}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
