from flask import Flask, jsonify, send_from_directory, request
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
    return jsonify({'members': filtered, 'chamber': chamber, 'total': len(filtered)})

@app.route('/api/member/<bioguide_id>/bills')
def get_member_bills(bioguide_id):
    limit = request.args.get('limit', 50)
    offset = request.args.get('offset', 0)
    url = f'{CONGRESS_BASE}/member/{bioguide_id}/sponsored-legislation?limit={limit}&offset={offset}&api_key={API_KEY}&{FMT}'
    r = requests.get(url)