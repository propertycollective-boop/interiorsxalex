import os
import time
import urllib.request
import urllib.error
import json
from html import escape
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


def send_via_web3forms(subject, name, email, phone, project_type, location, timeline, message):
    api_key = os.environ.get('WEB3FORMS_KEY', '')
    if not api_key:
        raise ValueError('WEB3FORMS_KEY not set')

    body_text = f"""
Name: {name}
Email: {email}
Phone: {phone or '—'}

Project Type: {project_type or '—'}
Location: {location or '—'}
Timeline: {timeline or '—'}

Message:
{message or 'No message provided.'}
    """.strip()

    payload = {
        'access_key': api_key,
        'subject': subject,
        'from_name': 'Interiors x Alex',
        'name': name,
        'email': email,
        'message': body_text,
        'botcheck': ''
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        'https://api.web3forms.com/submit',
        data=data,
        headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


@app.route('/api/contact/test')
def contact_test():
    api_key = os.environ.get('WEB3FORMS_KEY')
    if not api_key:
        return jsonify({'status': 'error', 'reason': 'WEB3FORMS_KEY not set on Render'}), 500
    try:
        result = send_via_web3forms(
            subject='Test — Interiors x Alex',
            name='Test', email='test@test.com',
            phone='', project_type='', location='', timeline='',
            message='This is a test submission.'
        )
        return jsonify({'status': 'ok', 'result': result})
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return jsonify({'status': 'error', 'reason': f'HTTP {e.code}: {body}'}), 500
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

    if not os.environ.get('WEB3FORMS_KEY'):
        print('WEB3FORMS_KEY not set')
        return jsonify({'error': 'Server email not configured.'}), 500

    subject = f'New Inquiry from {name} — Interiors x Alex'

    try:
        send_via_web3forms(subject, name, email, phone, project_type, location, timeline, message)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f'Web3Forms error {e.code}: {body}')
        return jsonify({'error': 'Failed to send. Please email design@interiorsxalex.com directly.'}), 500
    except Exception as e:
        print(f'Web3Forms error: {type(e).__name__}: {e}')
        return jsonify({'error': 'Failed to send. Please email design@interiorsxalex.com directly.'}), 500

    return jsonify({'success': True}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
