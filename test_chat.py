import urllib.request, json
data = json.dumps({'character_id': 'detective_hale', 'story_id': 'demo', 'branch_id': 'canon', 'sequence': 5, 'message': 'What do you know about the murder?'}).encode()
req = urllib.request.Request('http://127.0.0.1:8000/api/chat/', data=data, headers={'Content-Type': 'application/json'})
try:
    r = urllib.request.urlopen(req)
    result = json.loads(r.read())
    print('Success:', result['success'])
    print('Output:', result['output'][:200])
except Exception as e:
    err = e.read().decode() if hasattr(e, 'read') else str(e)
    print('Error:', err)
