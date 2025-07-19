def test_logout_success(client, auth_header):
  """
  正常系: 認証済みユーザーがログアウトAPIにアクセスし、成功メッセージが返ることをテスト
  """
  response = client.post('/api/v1/logout', headers=auth_header)
  data = response.get_json()

  assert response.status_code == 200
  assert data['message'] == 'ログアウトに成功しました'

def test_logout_no_token(client):
  """
  異常系: JWTトークンなしでアクセスした場合に401エラーが返ることをテスト
  """
  response = client.post('/api/v1/logout')
  data = response.get_json()

  assert response.status_code == 401
  assert data['msg'] == 'Missing Authorization Header'

def test_logout_invalid_token(client):
  """
  異常系: 無効なJWTトークンでアクセスした場合に422エラーが返ることをテスト
  """
  headers = {
      'Authorization': 'Bearer invalidtoken'
  }
  response = client.post('/api/v1/logout', headers=headers)
  data = response.get_json()

  assert response.status_code == 422
  assert data['msg'] == 'Not enough segments'