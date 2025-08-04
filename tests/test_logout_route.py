from .helpers import create_test_user, get_auth_header

# ----------------------------------------------
#      <<-- テストの要件 -->>

# 正常にログアウト出来たら200が返ってくるか
# トークン無しだと拒否されるか
# 無効なトークンだと拒否されるか
# ----------------------------------------------
  
def test_logout_success(client):
  """正常系: 有効なトークンでログアウトが成功することをテスト"""
  with client.application.app_context():
    # テスト用のユーザーを作成し、そのユーザーの認証ヘッダーを取得
    user = create_test_user()
    auth_header = get_auth_header(user.id)

  response = client.post('/api/v1/logout', headers=auth_header)
  assert response.status_code == 200
  data = response.get_json()
  assert data['message'] == 'ログアウトに成功しました'

def test_logout_without_token(client):
  """異常系: トークンなしでアクセスした場合に401エラーが返ることをテスト"""
  response = client.post('/api/v1/logout')
  data = response.get_json()
  assert response.status_code == 401
  # __init__.py で設定したカスタムエラーメッセージを検証
  assert data['message'] == 'リクエストには認証トークンが必要です'

def test_logout_with_invalid_token(client):
  """異常系: 無効なトークンでアクセスした場合に422エラーが返ることをテスト"""
  response = client.post(
    '/api/v1/logout',
    headers={'Authorization': 'Bearer invalid.token.here'}
  )
  data = response.get_json()
  assert response.status_code == 422
  assert data['message'] == '無効な認証トークンです'