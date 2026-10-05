import os
import time
import smtplib
import urllib.request
import urllib.error
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from html import escape
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')

_ig_cache = {'data': None, 'ts': 0}
IG_CACHE_TTL = 3600


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

@app.route('/portfolio/new-jersey-residence')
def case_study_nj():
    return send_from_directory('portfolio', 'new-jersey-residence.html')

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


def build_email_html(name, email, phone, project_type, location, timeline, message):
    def row(label, value):
        if not value:
            return ''
        return f'''
        <tr>
          <td style="padding:10px 16px;background:#f9f6f1;border-bottom:1px solid #ede8df;
                     width:140px;font-family:Georgia,serif;font-size:12px;
                     color:#8a7b6b;letter-spacing:0.08em;text-transform:uppercase;
                     vertical-align:top;">{label}</td>
          <td style="padding:10px 16px;border-bottom:1px solid #ede8df;
                     font-family:Georgia,serif;font-size:14px;color:#2c2418;
                     vertical-align:top;">{escape(value)}</td>
        </tr>'''

    message_html = escape(message).replace('\n', '<br>') if message else 'No message provided.'

    return f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f0ea;font-family:Georgia,serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f0ea;padding:40px 20px;">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

      <!-- Header -->
      <tr>
        <td style="background:#2c2418;padding:36px 40px;text-align:center;">
          <p style="margin:0;font-family:Georgia,serif;font-size:11px;color:#c9b99a;
                    letter-spacing:0.2em;text-transform:uppercase;">Interiors x Alex</p>
          <p style="margin:12px 0 0;font-family:Georgia,serif;font-size:22px;
                    color:#f9f6f1;font-weight:normal;font-style:italic;">New Inquiry</p>
        </td>
      </tr>

      <!-- Intro -->
      <tr>
        <td style="background:#ffffff;padding:28px 40px 20px;
                   border-left:1px solid #ede8df;border-right:1px solid #ede8df;">
          <p style="margin:0;font-family:Georgia,serif;font-size:14px;color:#8a7b6b;
                    line-height:1.6;">
            A new project inquiry was submitted through <strong>interiorsxalex.com</strong>.
          </p>
        </td>
      </tr>

      <!-- Detail rows -->
      <tr>
        <td style="background:#ffffff;padding:0 40px 8px;
                   border-left:1px solid #ede8df;border-right:1px solid #ede8df;">
          <table width="100%" cellpadding="0" cellspacing="0"
                 style="border:1px solid #ede8df;border-radius:4px;overflow:hidden;">
            {row('Name', name)}
            {row('Email', email)}
            {row('Phone', phone)}
            {row('Project Type', project_type)}
            {row('Location', location)}
            {row('Timeline', timeline)}
          </table>
        </td>
      </tr>

      <!-- Message -->
      <tr>
        <td style="background:#ffffff;padding:20px 40px 32px;
                   border-left:1px solid #ede8df;border-right:1px solid #ede8df;">
          <p style="margin:0 0 8px;font-family:Georgia,serif;font-size:11px;color:#8a7b6b;
                    letter-spacing:0.12em;text-transform:uppercase;">Message</p>
          <p style="margin:0;font-family:Georgia,serif;font-size:14px;color:#2c2418;
                    line-height:1.7;white-space:pre-wrap;">{message_html}</p>
        </td>
      </tr>

      <!-- Reply CTA -->
      <tr>
        <td style="background:#f9f6f1;padding:24px 40px;text-align:center;
                   border:1px solid #ede8df;border-top:none;">
          <a href="mailto:{escape(email)}"
             style="display:inline-block;padding:12px 32px;background:#2c2418;
                    color:#f9f6f1;font-family:Georgia,serif;font-size:13px;
                    letter-spacing:0.1em;text-decoration:none;border-radius:2px;">
            Reply to {escape(name.split()[0] if name else 'Client')}
          </a>
        </td>
      </tr>

      <!-- Footer -->
      <tr>
        <td style="padding:20px 40px;text-align:center;">
          <p style="margin:0;font-family:Georgia,serif;font-size:11px;color:#b0a090;
                    letter-spacing:0.08em;">
            interiorsxalex.com &nbsp;·&nbsp; design@interiorsxalex.com
          </p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>'''


def send_email(to_email, subject, html, reply_to=None):
    smtp_user = os.environ.get('GMAIL_USER', '')
    smtp_pass = os.environ.get('GMAIL_APP_PASSWORD', '')
    if not smtp_user or not smtp_pass:
        raise ValueError('GMAIL_USER or GMAIL_APP_PASSWORD not set')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f'Interiors x Alex <{smtp_user}>'
    msg['To'] = to_email
    if reply_to:
        msg['Reply-To'] = reply_to
    msg.attach(MIMEText(html, 'html'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())


@app.route('/api/contact/test')
def contact_test():
    smtp_user = os.environ.get('GMAIL_USER')
    smtp_pass = os.environ.get('GMAIL_APP_PASSWORD')
    to_email = os.environ.get('CONTACT_EMAIL', 'design@interiorsxalex.com')
    if not smtp_user or not smtp_pass:
        return jsonify({'status': 'error', 'reason': 'GMAIL_USER or GMAIL_APP_PASSWORD not set'}), 500
    try:
        html = build_email_html('Test User', 'test@test.com', '(555) 555-5555',
                                'Full-Service Design', 'Colts Neck, NJ', 'ASAP',
                                'This is a test submission to verify email delivery.')
        send_email(to_email, 'Test — Interiors x Alex', html, reply_to='test@test.com')
        return jsonify({'status': 'ok', 'to': to_email})
    except Exception as e:
        return jsonify({'status': 'error', 'reason': f'{type(e).__name__}: {e}'}), 500


@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json(silent=True) or {}

    name         = escape(data.get('name', '').strip())
    email        = data.get('email', '').strip()
    phone        = escape(data.get('phone', '').strip())
    project_type = escape(data.get('project-type', '').strip())
    location     = escape(data.get('location', '').strip())
    timeline     = escape(data.get('timeline', '').strip())
    message      = escape(data.get('message', '').strip())

    if not name or not email:
        return jsonify({'error': 'Name and email are required.'}), 400

    smtp_user = os.environ.get('GMAIL_USER')
    smtp_pass = os.environ.get('GMAIL_APP_PASSWORD')
    if not smtp_user or not smtp_pass:
        print('GMAIL credentials not set')
        return jsonify({'error': 'Server email not configured.'}), 500

    to_email = os.environ.get('CONTACT_EMAIL', 'design@interiorsxalex.com')
    subject = f'New Inquiry from {name} — Interiors x Alex'
    html = build_email_html(name, email, phone, project_type, location, timeline, message)

    try:
        send_email(to_email, subject, html, reply_to=email)
    except Exception as e:
        print(f'Email error: {type(e).__name__}: {e}')
        return jsonify({'error': 'Failed to send message. Please email design@interiorsxalex.com directly.'}), 500

    return jsonify({'success': True}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
