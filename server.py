from flask import Flask, jsonify, send_from_directory, request
import requests
import os

app = Flask(__name__)

API_KEY = 'JXzprF4VnXjwKyN32rMdItQvdxUmNS5SapCFyTv8'
CONGRESS_BASE = 'https://api.congress.gov/v3'
CONGRESS = 119
FMT = 'format=json'
TIMEOUT = 10

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/members/<chamber>')
def get_members(chamber):
    all_members = []
    offset = 0
    limit = 250
    while True:
        url = f'{CONGRESS_BASE}/member/congress/{CONGRESS}?limit={limit}&offset={offset}&currentMember=true&api_key={API_KEY}&{FMT}'
        r = requests.get(url, timeout=TIMEOUT)
        data = r.json()
        members = data.get('members', [])
        if not members:
            break
        all_members.extend(members)
        total = data.get('pagination', {}).get('count', 0)
        offset += limit
        if offset >= total:
            break
    if chamber == 'senate':
        filtered = [m for m in all_members if not m.get('district')]
        filtered = sorted(filtered, key=lambda m: m.get('name', ''))[:100]
    else:
        filtered = [m for m in all_members if m.get('district')]
    for m in filtered:
        m['_chamber'] = chamber
    return jsonify({'members': filtered, 'chamber': chamber, 'total': len(filtered)})

@app.route('/api/member/<bioguide_id>/bills')
def get_member_bills(bioguide_id):
    try:
        limit = request.args.get('limit', 50)
        offset = request.args.get('offset', 0)
        url = f'{CONGRESS_BASE}/member/{bioguide_id}/sponsored-legislation?limit={limit}&offset={offset}&api_key={API_KEY}&{FMT}'
        r = requests.get(url, timeout=TIMEOUT)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e), 'sponsoredLegislation': []}), 200

@app.route('/api/member/<bioguide_id>/detail')
def get_member_detail(bioguide_id):
    try:
        url = f'{CONGRESS_BASE}/member/{bioguide_id}?api_key={API_KEY}&{FMT}'
        r = requests.get(url, timeout=TIMEOUT)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e), 'member': {}}), 200

@app.route('/api/member/<bioguide_id>/committees')
def get_member_committees(bioguide_id):
    try:
        url = f'{CONGRESS_BASE}/member/{bioguide_id}?api_key={API_KEY}&{FMT}'
        r = requests.get(url, timeout=TIMEOUT)
        data = r.json()
        member = data.get('member', {})
        committees = []
        if member.get('committeeAssignments'):
            for c in member['committeeAssignments'].get('item', []):
                committees.append({
                    'name': c.get('committee', {}).get('name', ''),
                    'role': c.get('rank', 'Member')
                })
        return jsonify({'committees': committees, 'bioguideId': bioguide_id})
    except Exception as e:
        return jsonify({'committees': [], 'error': str(e)}), 200

@app.route('/api/bills/recent')
def get_recent_bills():
    try:
        url = f'{CONGRESS_BASE}/bill/{CONGRESS}?limit=20&sort=updateDate+desc&api_key={API_KEY}&{FMT}'
        r = requests.get(url, timeout=TIMEOUT)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e), 'bills': []}), 200

@app.route('/api/votes/recent')
def get_recent_votes():
    try:
        url = f'{CONGRESS_BASE}/vote/congress/{CONGRESS}?limit=20&api_key={API_KEY}&{FMT}'
        r = requests.get(url, timeout=TIMEOUT)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e), 'votes': []}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)