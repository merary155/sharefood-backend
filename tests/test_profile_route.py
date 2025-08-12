from sharefood import db
from .helpers import create_test_user, get_auth_header

# ----------------------------------------------
#      <<-- テストの要件 -->>

# 正常にログアウト出来たら200が返ってくるか
# トークン無しだと拒否されるか
# 無効なトークンだと拒否されるか
# 存在しないユーザーでアクセスしたら拒否されるか
# ----------------------------------------------

def test_get_profile_success(client):
  """
  正常系: 認証済みユーザーがプロフィールを正常に取得できることをテスト
  """
  with client.application.app_context():
    # DB操作はアプリケーションコンテキスト内で行う
    test_user = create_test_user() # conftestからヘルパー関数を呼び出し
    auth_header = get_auth_header(test_user.id) # conftestからヘルパー関数を呼び出し

  response = client.get('/api/v1/me', headers=auth_header)
  data = response.get_json()

  assert response.status_code == 200
  assert data['message'] == 'プロフィールを取得しました'
  assert 'user' in data
  assert data['user']['id'] == test_user.id
  assert data['user']['username'] == test_user.username
  assert data['user']['email_address'] == test_user.email_address

def test_get_profile_no_token(client):
  """
  異常系: JWTトークンなしでアクセスした場合に401エラーが返ることをテスト
  """
  response = client.get('/api/v1/me')
  data = response.get_json()

  assert response.status_code == 401
  # __init__.pyで設定したカスタムエラーメッセージ
  assert data['message'] == 'リクエストには認証トークンが必要です'

def test_get_profile_invalid_token(client):
  """
  異常系: 無効なJWTトークンでアクセスした場合に422エラーが返ることをテスト
  """
  headers = {
    'Authorization': 'Bearer invalidtoken'
  }
  response = client.get('/api/v1/me', headers=headers)
  data = response.get_json()

  # __init__.pyで設定したカスタムエラーメッセージ
  assert response.status_code == 422
  assert data['message'] == '無効な認証トークンです'

def test_get_profile_user_not_found(client):
  """
  異常系: トークンは有効だが、対応するユーザーがDBに存在しない場合に404エラーが返ることをテスト
  """
  with client.application.app_context():
    # テスト用のユーザーを作成し、IDを控える
    user = create_test_user(username="tempuser", email="temp@example.com") 
    user_id = user.id
    auth_header = get_auth_header(user_id) 
    # ユーザーをDBから削除
    db.session.delete(user)
    db.session.commit()

  response = client.get('/api/v1/me', headers=auth_header)
  data = response.get_json()
  
  assert response.status_code == 404
  assert data['message'] == 'ユーザーが見つかりません'