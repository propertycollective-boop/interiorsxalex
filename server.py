import os
import resend
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

    api_key = os.environ.get('RESEND_API_KEY')
    to_email = os.environ.get('CONTACT_EMAIL', 'interiorsxalex@gmail.com')

    if not api_key:
        print('RESEND_API_KEY not set')
        return jsonify({'error': 'Server email not configured.'}), 500

    resend.api_key = api_key

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

    try:
        resend.Emails.send({
            'from': 'Interiors x Alex <onboarding@resend.dev>',
            'to': to_email,
            'reply_to': email,
            'subject': f'New Inquiry from {name} — Interiors x Alex',
            'text': body,
        })
    except Exception as e:
        print(f'Email send error: {e}')
        return jsonify({'error': 'Failed to send message. Please try again.'}), 500

    return jsonify({'success': True}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
