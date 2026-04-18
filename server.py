from flask import Flask, jsonify, send_from_directory, request
import requests
import os
from urllib.parse import quote
import re
import json as json_lib

app = Flask(__name__)

API_KEY = 'JXzprF4VnXjwKyN32rMdItQvdxUmNS5SapCFyTv8'
FEC_KEY = 'FIuWmp66lcLynYUg5niiXOkOrb1UJxOx4wIspAO8'
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
CONGRESS_BASE = 'https://api.congress.gov/v3'
CONGRESS = 119
FMT = 'format=json'
TIMEOUT = 10

STATE_ABBR_MAP = {
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

@app.route('/api/member/<bioguide_id>/votes')
def get_member_votes(bioguide_id):
    try:
        print(f'Votes called for bioguide: {bioguide_id}')
        member_url = f'{CONGRESS_BASE}/member/{bioguide_id}?api_key={API_KEY}&{FMT}'
        member_r = requests.get(member_url, timeout=TIMEOUT)
        member_data = member_r.json().get('member', {})
        first_name = member_data.get('firstName', '')
        last_name = member_data.get('lastName', '')
        state_code = member_data.get('state', '')
        state_abbr = STATE_ABBR_MAP.get(state_code, state_code)
        print(f'Looking up votes for: {first_name} {last_name} ({state_abbr})')

        terms = member_data.get('terms', [])
        if isinstance(terms, dict):
            terms = terms.get('item', [])
        latest_term = terms[-1] if terms else {}
        role_type = 'senator' if latest_term.get('memberType') == 'Senator' else 'representative'

        search_url = f'https://www.govtrack.us/api/v2/role?current=true&state={state_abbr}&role_type={role_type}&format=json&limit=10'
        search_r = requests.get(search_url, timeout=TIMEOUT)
        print(f'GovTrack role search status: {search_r.status_code}')
        print(f'GovTrack response: {search_r.text[:400]}')
        roles = search_r.json().get('objects', [])

        matched = [r for r in roles if last_name.lower() in r.get('person', {}).get('lastname', '').lower()]
        role = matched[0] if matched else (roles[0] if roles else None)

        if not role:
            return jsonify({'error': 'Person not found on GovTrack', 'votes': []})

        person_obj = role.get('person', {})
        # person may be an integer ID or a dict
        if isinstance(person_obj, int):
            govtrack_id = person_obj
        elif isinstance(person_obj, dict):
            # Try direct id field first, then extract from link URL
            govtrack_id = person_obj.get('id')
            if not govtrack_id:
                link = person_obj.get('link', '')
                # link looks like: https://www.govtrack.us/congress/members/bernard_sanders/400357
                if link:
                    govtrack_id = link.rstrip('/').split('/')[-1]
        else:
            govtrack_id = role.get('person_id')
        print(f'GovTrack ID extracted: {govtrack_id}')
        
        votes_url = f'https://www.govtrack.us/api/v2/vote_voter?person={govtrack_id}&limit=20&format=json&order_by=-created'
        votes_r = requests.get(votes_url, timeout=TIMEOUT)
        print(f'Votes status: {votes_r.status_code}')
        vote_data = votes_r.json()

        votes = []
        for v in vote_data.get('objects', []):
            option = v.get('option', {})
            vote = v.get('vote', {})
            description = vote.get('question', '—') if isinstance(vote, dict) else '—'
            result = vote.get('result', '—') if isinstance(vote, dict) else '—'
            position = option.get('value', '—') if isinstance(option, dict) else '—'
            votes.append({
                'date': str(v.get('created', ''))[:10],
                'position': position,
                'description': description,
                'result': result,
                'passed': 'Passed' in result or 'Agreed' in result
            })

        return jsonify({
            'votes': votes,
            'total': vote_data.get('meta', {}).get('total_count', 0),
            'govtrack_id': govtrack_id
        })

    except Exception as e:
        print(f'Votes error: {e}')
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
        state_abbr = STATE_ABBR_MAP.get(state, state)
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

@app.route('/api/bill/summary')
def get_bill_summary():
    try:
        bill_type = request.args.get('type', '')
        bill_number = request.args.get('number', '')
        bill_congress = request.args.get('congress', CONGRESS)
        bill_title = request.args.get('title', '')

        bill_url = f'{CONGRESS_BASE}/bill/{bill_congress}/{bill_type.lower()}/{bill_number}?api_key={API_KEY}&{FMT}'
        bill_r = requests.get(bill_url, timeout=TIMEOUT)
        bill_data = bill_r.json().get('bill', {})

        summary_url = f'{CONGRESS_BASE}/bill/{bill_congress}/{bill_type.lower()}/{bill_number}/summaries?api_key={API_KEY}&{FMT}'
        summary_r = requests.get(summary_url, timeout=TIMEOUT)
        summaries = summary_r.json().get('summaries', [])
        official_summary = summaries[-1].get('text', '') if summaries else ''
        official_summary = re.sub(r'<[^>]+>', ' ', official_summary).strip()

        latest_action = bill_data.get('latestAction', {}).get('text', '')
        policy_area = bill_data.get('policyArea', {}).get('name', '')
        sponsors = bill_data.get('sponsors', [{}])
        sponsor_name = f"{sponsors[0].get('firstName', '')} {sponsors[0].get('lastName', '')}" if sponsors else ''
        sponsor_party = sponsors[0].get('party', '') if sponsors else ''

        context = f"""Bill: {bill_type} {bill_number} - {bill_title}
Policy Area: {policy_area}
Sponsor: {sponsor_name} ({sponsor_party})
Latest Action: {latest_action}
Official Summary: {official_summary[:3000] if official_summary else 'Not available'}"""

        claude_response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'Content-Type': 'application/json',
                'x-api-key': ANTHROPIC_KEY,
                'anthropic-version': '2023-06-01'
            },
            json={
                'model': 'claude-sonnet-4-6',
                'max_tokens': 1000,
                'system': 'You are a nonpartisan civic transparency tool. Analyze bills objectively. Return ONLY valid JSON with these exact fields: {"plain_summary": "2-3 sentence plain English summary", "teaser": "First sentence only - a hook", "key_provisions": ["provision 1", "provision 2"], "hidden_provisions": ["any unrelated provisions"], "who_benefits": "Plain assessment", "complexity": "simple|moderate|complex"}',
                'messages': [{'role': 'user', 'content': f'Analyze this bill:\n{context}'}]
            },
            timeout=30
        )

        print(f'Claude status: {claude_response.status_code}')
        text = ''.join(b.get('text', '') for b in claude_response.json().get('content', []))
        text = re.sub(r'```json|```', '', text).strip()
        analysis = json_lib.loads(text)

        return jsonify({
            'success': True,
            'analysis': analysis,
            'bill_info': {
                'title': bill_title,
                'type': bill_type,
                'number': bill_number,
                'policy_area': policy_area,
                'sponsor': sponsor_name,
                'latest_action': latest_action
            }
        })

    except Exception as e:
        print(f'Bill summary error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
