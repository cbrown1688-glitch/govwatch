
from flask import Flask, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)

API_KEY = 'JXzprF4VnXjwKyN32rMdItQvdxUmNS5SapCFyTv8'
CONGRESS_BASE = 'https://api.congress.gov/v3'
CONGRESS = 119
FMT = 'format=json'

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
        r = requests.get(url)
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

    print(f"Chamber: {chamber}, After filter: {len(filtered)}")
    return jsonify({'members': filtered, 'chamber': chamber, 'total': len(filtered)})

@app.route('/api/member/<bioguide_id>/bills')
def get_member_bills(bioguide_id):
    from flask import request
    limit = request.args.get('limit', 50)
    offset = request.args.get('offset', 0)
    url = f'{CONGRESS_BASE}/member/{bioguide_id}/sponsored-legislation?limit={limit}&offset={offset}&api_key={API_KEY}&{FMT}'
    r = requests.get(url)
    return jsonify(r.json())

@app.route('/api/member/<bioguide_id>/detail')
def get_member_detail(bioguide_id):
    url = f'{CONGRESS_BASE}/member/{bioguide_id}?api_key={API_KEY}&{FMT}'
    r = requests.get(url)
    return jsonify(r.json())

@app.route('/api/bills/recent')
def get_recent_bills():
    url = f'{CONGRESS_BASE}/bill/{CONGRESS}?limit=20&sort=updateDate+desc&api_key={API_KEY}&{FMT}'
    r = requests.get(url)
    data = r.json()
    # Log first bill structure so we can see available fields
    if data.get('bills'):
        import json
        print("BILL FIELDS:", list(data['bills'][0].keys()))
        print("SAMPLE BILL:", json.dumps(data['bills'][0], indent=2)[:500])
    return jsonify(data)

@app.route('/api/member/<bioguide_id>/committees')
def get_member_committees(bioguide_id):
    url = f'{CONGRESS_BASE}/member/{bioguide_id}?api_key={API_KEY}&{FMT}'
    r = requests.get(url)
    data = r.json()
    member = data.get('member', {})
    # Extract committee info from member detail
    committees = []
    if member.get('committeeAssignments'):
        for c in member['committeeAssignments'].get('item', []):
            committees.append({
                'name': c.get('committee', {}).get('name', ''),
                'role': c.get('rank', 'Member')
            })
    return jsonify({'committees': committees, 'bioguideId': bioguide_id})

@app.route('/api/votes/recent')
def get_recent_votes():
    url = f'{CONGRESS_BASE}/vote/congress/{CONGRESS}?limit=20&sort=date+desc&api_key={API_KEY}&{FMT}'
    r = requests.get(url)
    return jsonify(r.json())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)