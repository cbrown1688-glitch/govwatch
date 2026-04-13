from flask import Flask, jsonify, send_from_directory, request
import requests
import os
from urllib.parse import quote

app = Flask(__name__)

API_KEY = 'JXzprF4VnXjwKyN32rMdItQvdxUmNS5SapCFyTv8'
FEC_KEY = 'FIuWmp66lcLynYUg5niiXOkOrb1UJxOx4wIspAO8'
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
    total = 999
    while offset < total:
        url = f'{CONGRESS_BASE}/member/congress/{CONGRESS}?limit={limit}&offset={offset}&currentMember=true&api_key={API_KEY}&{FMT}'
        r = requests.get(url, timeout=TIMEOUT)
        data = r.json()
        members = data.get('members', [])
        if not members:
            break
        all_members.extend(members)
        total = data.get('pagination', {}).get('count', 999)
        print(f'Fetched offset {offset}, got {len(members)}, total={total}, accumulated={len(all_members)}')
        offset += limit

    def get_member_chamber(m):
        terms = m.get('terms', [])
        if isinstance(terms, dict):
            terms = terms.get('item', [])
        if terms:
            current = next((t for t in terms if t.get('congress') == 119), None)
            check = current or terms[-1]
            if isinstance(check, dict):
                ch = check.get('chamber', '')
                if ch == 'Senate':
                    return 'senate'
                if ch == 'House of Representatives':
                    return 'house'
        district = m.get('district')
        if district is not None and str(district) not in ['0', 'None', '']:
            return 'house'
        return 'senate'

    filtered = [m for m in all_members if get_member_chamber(m) == chamber]
    print(f'After filter: {len(filtered)} {chamber} members from {len(all_members)} total')

    if chamber == 'senate':
        filtered = sorted(filtered, key=lambda m: m.get('name', ''))[:100]
    
    for m in filtered:
        m['_chamber'] = chamber

    return jsonify({'members': filtered, 'chamber': chamber, 'total': len(filtered)})

@app.route('/api/member/<bioguide_id>/bills')
def get_member_bills(bioguide_id):
    try:
        offset = int(request.args.get('offset', 0))
        all_bills = []
        current_offset = offset
        limit = 100
        max_attempts = 5
        data = {}
        for _ in range(max_attempts):
            url = f'{CONGRESS_BASE}/member/{bioguide_id}/sponsored-legislation?limit={limit}&offset={current_offset}&api_key={API_KEY}&{FMT}'
            r = requests.get(url, timeout=TIMEOUT)
            data = r.json()
            items = data.get('sponsoredLegislation', [])
            if not items:
                break
            real_bills = [b for b in items if b.get('title') and b.get('type') and b.get('number')]
            all_bills.extend(real_bills)
            if len(all_bills) >= 50:
                break
            current_offset += limit
            total = data.get('pagination', {}).get('count', 0)
            if current_offset >= total:
                break
        return jsonify({
            'sponsoredLegislation': all_bills[:50],
            'pagination': {'count': data.get('pagination', {}).get('count', len(all_bills))}
        })
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

@app.route('/api/member/<bioguide_id>/funding')
def get_member_funding(bioguide_id):
    try:
        member_url = f'{CONGRESS_BASE}/member/{bioguide_id}?api_key={API_KEY}&{FMT}'
        member_r = requests.get(member_url, timeout=TIMEOUT)
        member_data = member_r.json().get('member', {})
        name = member_data.get('directOrderName', '')
        state = member_data.get('state', '')
        if not name:
            return jsonify({'error': 'Member not found', 'candidate': None, 'totals': {}, 'industries': []})
        last_name = name.split(',')[0].strip() if ',' in name else name.split()[-1]
        state_abbr_map = {
            'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
            'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA',
            'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS',
            'Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA',
            'Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT',
            'Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM',
            'New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK',
            'Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC',
            'South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT',
            'Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'
        }
        state_abbr = state_abbr_map.get(state, state)
        print(f'Searching FEC for: {last_name} in {state_abbr}')
        search_url = f'https://api.open.fec.gov/v1/candidates/?q={quote(last_name)}&state={state_abbr}&has_raised_funds=true&api_key={FEC_KEY}&per_page=10'
        search_r = requests.get(search_url, timeout=TIMEOUT)
        candidates = search_r.json().get('results', [])
        print(f'FEC candidates found: {len(candidates)}')
        for c in candidates:
            print(f'  - {c.get("name")} ({c.get("candidate_id")})')
        if not candidates:
            return jsonify({'error': 'No FEC candidate found', 'candidate': None, 'totals': {}, 'industries': []})
        senate_matches = [c for c in candidates if c.get('candidate_id', '').startswith('S') and c.get('name', '').upper().startswith(last_name.upper())]
        house_matches = [c for c in candidates if c.get('name', '').upper().startswith(last_name.upper())]
        if senate_matches:
            candidate = senate_matches[0]
        elif house_matches:
            candidate = house_matches[0]
        else:
            candidate = candidates[0]
        print(f'Selected candidate: {candidate.get("name")} ({candidate.get("candidate_id")})')
        candidate_id = candidate.get('candidate_id')
        totals_url = f'https://api.open.fec.gov/v1/candidate/{candidate_id}/totals/?api_key={FEC_KEY}&per_page=1'
        totals_r = requests.get(totals_url, timeout=TIMEOUT)
        print(f'Totals status: {totals_r.status_code}')
        if totals_r.status_code == 200 and totals_r.text:
            totals = totals_r.json().get('results', [{}])[0]
        else:
            summary_url = f'https://api.open.fec.gov/v1/candidates/?candidate_id={candidate_id}&api_key={FEC_KEY}&per_page=1'
            summary_r = requests.get(summary_url, timeout=TIMEOUT)
            candidate_detail = summary_r.json().get('results', [{}])[0]
            totals = {
                'receipts': candidate_detail.get('receipts', 0),
                'disbursements': candidate_detail.get('disbursements', 0),
                'last_cash_on_hand_end_period': candidate_detail.get('cash_on_hand_end_period', 0),
                'cycle': candidate_detail.get('election_year', '')
            }
        industries = []
        comm_url = f'https://api.open.fec.gov/v1/candidate/{candidate_id}/committees/?api_key={FEC_KEY}&designation=P'
        comm_r = requests.get(comm_url, timeout=TIMEOUT)
        if comm_r.status_code == 200 and comm_r.text:
            comms = comm_r.json().get('results', [])
            if comms:
                committee_id = comms[0].get('committee_id')
                donors_url = f'https://api.open.fec.gov/v1/schedules/schedule_a/?committee_id={committee_id}&api_key={FEC_KEY}&per_page=10&sort=-contribution_receipt_amount&two_year_transaction_period=2024&is_individual=false'
                donors_r = requests.get(donors_url, timeout=TIMEOUT)
                if donors_r.status_code == 200 and donors_r.text:
                    donor_results = donors_r.json().get('results', [])
                    industries = [{'industry_name': d.get('contributor_name', 'Unknown'), 'total': d.get('contribution_receipt_amount', 0)} for d in donor_results]
        return jsonify({'candidate': candidate, 'totals': totals, 'industries': industries})
    except Exception as e:
        print(f'Funding error: {e}')
        return jsonify({'error': str(e), 'candidate': None, 'totals': {}, 'industries': []}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)