from flask_jwt_extended import create_access_token
from sharefood.models import User
from sharefood import db

# ----------------------------------------------
#      <<-- テストの要件 -->>

# 正常にログアウト出来たら200が返ってくるか
# トークン無しだと拒否されるか
# 無効なトークンだと拒否されるか
# 存在しないユーザーでアクセスしたら拒否されるか
# ----------------------------------------------

def create_test_user(username="testuser", email="test@example.com", password="password"):
  """テスト用のユーザーをDBに作成するヘルパー関数"""
  user = User(username=username, email_address=email)
  user.password = password
  db.session.add(user)
  db.session.commit()
  return user

def test_get_profile_success(client):
  """
  正常系: 認証済みユーザーがプロフィールを正常に取得できることをテスト
  """
  with client.application.app_context():
    # DB操作はアプリケーションコンテキスト内で行う
    test_user = create_test_user()
    access_token = create_access_token(identity=str(test_user.id))
    
  response = client.get(
    '/api/v1/me', 
    headers={'Authorization': f'Bearer {access_token}'}
    )
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
    access_token = create_access_token(identity=str(user_id))
    # ユーザーをDBから削除
    db.session.delete(user)
    db.session.commit()

  headers = {'Authorization': f'Bearer {access_token}'}
  response = client.get('/api/v1/me', headers=headers)
  data = response.get_json()
  
  assert response.status_code == 404
  assert data['message'] == 'ユーザーが見つかりません'