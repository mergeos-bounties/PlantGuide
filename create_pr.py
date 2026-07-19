#!/usr/bin/env python3
import json, os, urllib.request, urllib.error, sys
from datetime import datetime, timezone

# Source GIT_TOKEN
GIT_TOKEN = os.environ.get('GIT_TOKEN')
if not GIT_TOKEN:
    with open('/opt/data/.hermes/.env', 'r') as f:
        for line in f:
            if line.startswith('GIT_TOKEN='):
                GIT_TOKEN = line.strip().split('=', 1)[1]
                break

if not GIT_TOKEN:
    print('GIT_TOKEN not found. Exiting.')
    sys.exit(1)

print(f'GIT_TOKEN loaded: {GIT_TOKEN[:8]}... (len: {len(GIT_TOKEN)})')

# Load state
with open('/opt/data/cron/state/mergeos-in-progress.json', 'r') as f:
    state = json.load(f)

if not state or not state.get('repo'):
    print('No in-progress state found. Exiting.')
    sys.exit(0)

repo = state['repo']
issue_num = state['issue']
# Override branch with the actual branch we used
branch = 'fix/issue-18-contributing-md'

# Fetch issue details to get title and body for PR
issue_url = f'https://api.github.com/repos/mergeos-bounties/{repo}/issues/{issue_num}'
headers = {'Authorization': f'token {GIT_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}

try:
    req = urllib.request.Request(issue_url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        issue_data = json.loads(resp.read().decode('utf-8'))
    pr_title = issue_data.get('title')
    pr_body = (issue_data.get('body') or '') + f'\n\nFixes #{issue_num}'
except Exception as e:
    print(f'Error fetching issue details: {e}')
    pr_title = f'Fix issue {issue_num}'
    pr_body = f'Automated PR for issue #{issue_num}.'

print(f'Issue title: {pr_title}')
print(f'Branch: {branch}')

# Create PR
api_url = f'https://api.github.com/repos/mergeos-bounties/{repo}/pulls'
payload = {
    'title': pr_title,
    'body': pr_body,
    'head': f'CloneBro:{branch}',
    'base': 'master'
}

pr_req = urllib.request.Request(api_url, headers=headers, method='POST')
pr_req.data = json.dumps(payload).encode('utf-8')
try:
    with urllib.request.urlopen(pr_req) as resp:
        pr_data = json.loads(resp.read().decode('utf-8'))
    pr_url = pr_data.get('html_url')
    print(f'PR created: {pr_url}')
except urllib.error.HTTPError as e:
    print(f'HTTP Error creating PR: {e.code} {e.reason}')
    error_body = e.read().decode('utf-8')
    print(f'Error body: {error_body}')
    sys.exit(1)
except Exception as e:
    print(f'Error creating PR: {e}')
    sys.exit(1)

# Update state
state['branch'] = branch
state['pr_url'] = pr_url
with open('/opt/data/cron/state/mergeos-in-progress.json', 'w') as f:
    json.dump(state, f, indent=2)

# Claim on the issue itself
comment_body = 'I claim this bounty'
print('Claiming on issue...')
comment_url = f'https://api.github.com/repos/mergeos-bounties/{repo}/issues/{issue_num}/comments'
comment_req = urllib.request.Request(comment_url, headers=headers, method='POST')
comment_req.data = json.dumps({'body': comment_body}).encode('utf-8')
try:
    urllib.request.urlopen(comment_req)
    print(f'Claimed issue #{issue_num}')
    claimed_issue = True
except Exception as e:
    print(f'Failed to claim issue #{issue_num}: {e}')
    claimed_issue = False

# Claim on mergeos#1
print('Claiming on mergeos#1...')
comment_url_mrg1 = 'https://api.github.com/repos/mergeos-bounties/mergeos/issues/1/comments'
comment_req_mrg1 = urllib.request.Request(comment_url_mrg1, headers=headers, method='POST')
comment_req_mrg1.data = json.dumps({'body': comment_body}).encode('utf-8')
try:
    urllib.request.urlopen(comment_req_mrg1)
    print('Claimed mergeos#1')
    claimed_mergeos1 = True
except Exception as e:
    print(f'Failed to claim mergeos#1: {e}')
    claimed_mergeos1 = False

# Claim on mergeos#244
print('Claiming on mergeos#244...')
comment_url_mrg244 = 'https://api.github.com/repos/mergeos-bounties/mergeos/issues/244/comments'
comment_req_mrg244 = urllib.request.Request(comment_url_mrg244, headers=headers, method='POST')
comment_req_mrg244.data = json.dumps({'body': comment_body}).encode('utf-8')
try:
    urllib.request.urlopen(comment_req_mrg244)
    print('Claimed mergeos#244')
    claimed_mergeos244 = True
except Exception as e:
    print(f'Failed to claim mergeos#244: {e}')
    claimed_mergeos244 = False

# Update done list
done_item = f'mergeos-bounties/{repo}#{issue_num}'
if claimed_issue and claimed_mergeos1 and claimed_mergeos244:
    with open('/opt/data/cron/state/mergeos-done.json', 'r+') as f:
        done_data = json.load(f)
        if done_item not in done_data['done']:
            done_data['done'].append(done_item)
            # Add MRG based on reward (hardcoded for now)
            reward = 25  # For PlantGuide#18: [25 MRG] CONTRIBUTING.md + good-first-issue path
            done_data['total_mrg'] += reward
            done_data['last_run'] = datetime.now(timezone.utc).isoformat()
            print(f'Added {reward} MRG. Total MRG: {done_data["total_mrg"]}')
            f.seek(0)
            json.dump(done_data, f, indent=2)
            f.truncate()
        else:
            print(f'{done_item} already in done list.')

    # Clear in-progress state
    with open('/opt/data/cron/state/mergeos-in-progress.json', 'w') as f:
        f.write('null')
    print('In-progress state cleared.')
else:
    print('Not all claims successful, not updating done list or clearing in-progress.')

print('PR flow completed successfully.')