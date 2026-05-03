import urllib.request, json
req = urllib.request.Request('http://127.0.0.1:8000/api/token/', data=b'{"username": "admin", "password": "admin"}', headers={'Content-Type': 'application/json'})
try:
    resp = urllib.request.urlopen(req)
    token = json.loads(resp.read().decode())['access']
    req2 = urllib.request.Request('http://127.0.0.1:8000/api/deportistas/reporte_ingresos/', headers={'Authorization': 'Bearer ' + token})
    resp2 = urllib.request.urlopen(req2)
    print(resp2.read().decode())
except Exception as e:
    print(e)
