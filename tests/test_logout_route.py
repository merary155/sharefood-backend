from flask_jwt_extended import create_access_token
from sharefood import db
from sharefood.models import User

# ----------------------------------------------
#      <<-- テストの要件 -->>

# 正常にログアウト出来たら200が返ってくるか
# トークン無しだと拒否されるか
# 無効なトークンだと拒否されるか
# ----------------------------------------------
  
def test_logout_success(client):
  """正常系: 有効なトークンでログアウトが成功することをテスト"""
  test_user_id = 1
  # client.application で conftest の app インスタンスにアクセスできる
  with client.application.app_context():
    # このテストではDBのユーザーは不要だが、トークン生成のために便宜上IDを使う
    # 実際のログアウトAPIはDBを見ないので、ユーザーが存在しなくても動作する
    access_token = create_access_token(identity=str(test_user_id))
  response = client.post(
    '/api/v1/logout',
    headers={'Authorization': f'Bearer {access_token}'}
  )
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