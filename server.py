import os
import time
import smtplib
import urllib.request
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')

_ig_cache = {'data': None, 'ts': 0}
IG_CACHE_TTL = 3600  # 1 hour

def fetch_instagram_posts():
    page_token = os.environ.get('IG_PAGE_TOKEN', '')
    ig_id = os.environ.get('IG_ACCOUNT_ID', '17841464471266561')
    if not page_token:
        return []
    url = (f'https://graph.facebook.com/v19.0/{ig_id}/media'
           f'?fields=id,media_type,media_url,thumbnail_url,permalink,timestamp,caption'
           f'&limit=12&access_token={page_token}')
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return json.loads(r.read()).get('data', [])
    except Exception as e:
        print(f'Instagram fetch error: {e}')
        return []

@app.route('/api/instagram')
def instagram_feed():
    global _ig_cache
    if _ig_cache['data'] is None or time.time() - _ig_cache['ts'] > IG_CACHE_TTL:
        _ig_cache['data'] = fetch_instagram_posts()
        _ig_cache['ts'] = time.time()
    return jsonify(_ig_cache['data'])


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/about')
def about():
    return send_from_directory('.', 'about.html')

@app.route('/services')
def services():
    return send_from_directory('.', 'services.html')

@app.route('/portfolio')
def portfolio():
    return send_from_directory('.', 'portfolio.html')

@app.route('/contact')
def contact_page():
    return send_from_directory('.', 'contact.html')

@app.route('/privacy')
def privacy():
    return send_from_directory('.', 'privacy.html')

@app.route('/terms')
def terms():
    return send_from_directory('.', 'terms.html')

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

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ margin: 0; padding: 0; background: #F5F0E8; font-family: Georgia, serif; }}
    .wrap {{ max-width: 560px; margin: 40px auto; background: #FBF9F5; border: 1px solid #DDD5C5; }}
    .header {{ background: #2A2218; padding: 36px 40px; }}
    .header p {{ margin: 0; font-family: Arial, sans-serif; font-size: 10px; letter-spacing: 3px; text-transform: uppercase; color: #C4AE96; }}
    .header h1 {{ margin: 8px 0 0; font-family: Georgia, serif; font-size: 22px; font-weight: normal; color: #FBF9F5; }}
    .body {{ padding: 40px; }}
    .label {{ font-family: Arial, sans-serif; font-size: 9px; letter-spacing: 2.5px; text-transform: uppercase; color: #9E8E7A; margin-bottom: 4px; }}
    .value {{ font-size: 15px; color: #2A2218; margin: 0 0 28px; font-family: Georgia, serif; }}
    .divider {{ border: none; border-top: 1px solid #DDD5C5; margin: 4px 0 28px; }}
    .message-box {{ background: #F5F0E8; border-left: 3px solid #C4AE96; padding: 20px 24px; margin-top: 4px; }}
    .message-box p {{ font-size: 14px; color: #7A6E60; line-height: 1.8; margin: 0; font-family: Georgia, serif; }}
    .footer {{ background: #EAE3D5; padding: 20px 40px; font-family: Arial, sans-serif; font-size: 10px; letter-spacing: 1px; color: #9E8E7A; text-align: center; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <p>New Inquiry</p>
      <h1>Interiors x Alex</h1>
    </div>
    <div class="body">
      <p class="label">Name</p>
      <p class="value">{name}</p>
      <p class="label">Email</p>
      <p class="value">{email}</p>
      <p class="label">Phone</p>
      <p class="value">{phone or '—'}</p>
      <hr class="divider">
      <p class="label">Project Type</p>
      <p class="value">{project_type or '—'}</p>
      <p class="label">Location</p>
      <p class="value">{location or '—'}</p>
      <p class="label">Timeline</p>
      <p class="value">{timeline or '—'}</p>
      <hr class="divider">
      <p class="label">Message</p>
      <div class="message-box">
        <p>{message or 'No message provided.'}</p>
      </div>
    </div>
    <div class="footer">interiorsxalex.com</div>
  </div>
</body>
</html>
"""

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'New Inquiry from {name} — Interiors x Alex'
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Reply-To'] = email
    msg.attach(MIMEText(html, 'html'))

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
