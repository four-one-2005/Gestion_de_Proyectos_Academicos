import urllib.request
import json

def test_live_server():
    url = "http://127.0.0.1:8000/graphql"

    # 1. Login vía HTTP para obtener token
    login_payload = {
        "query": """
        mutation Login($u: String!, $p: String!) {
          tokenAuth(username: $u, password: $p) {
            token
            payload
          }
        }
        """,
        "variables": {"u": "estudiante_perez", "p": "password123"}
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(login_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read())
        print("1. Login HTTP Exitoso:", body)
        token = body['data']['tokenAuth']['token']
        assert token is not None

    # 2. Query protegida / autenticada con header Authorization: JWT <token>
    query_payload = {
        "query": """
        query {
          me {
            id
            username
            email
            rol { nombre }
          }
          proyectos {
            id
            titulo
            estado { nombre }
          }
        }
        """
    }
    req2 = urllib.request.Request(
        url,
        data=json.dumps(query_payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'JWT {token}'
        }
    )
    with urllib.request.urlopen(req2) as resp:
        body2 = json.loads(resp.read())
        print("\n2. Consulta HTTP Autenticada 'me' + 'proyectos':", body2)
        assert body2['data']['me']['username'] == 'estudiante_perez'

    print("\n>>> ¡EL SERVIDOR HTTP ESTÁ RESPONDIENDO PERFECTAMENTE CON GRAPHQL Y JWT!")

if __name__ == '__main__':
    test_live_server()
