from flask_jwt_extended import create_access_token
from sharefood.models import User
from sharefood import db
import pytest
from flask import Flask

@pytest.fixture
def app():
  app = Flask(__name__)

@pytest.fixture

  

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
    # 1. テスト用のユーザーを作成
    user = create_test_user()
    # 2. そのユーザーのアクセストークンを生成
    access_token = create_access_token(identity=str(user.id))

  # 3. プロフィール取得APIにリクエスト
  headers = {
    'Authorization': f'Bearer {access_token}'
  }
  response = client.get('/api/v1/profile', headers=headers)
  data = response.get_json()

  # 4. レスポンスを検証
  assert response.status_code == 200
  assert data['message'] == 'プロフィールを取得しました'
  assert 'user' in data
  assert data['user']['id'] == user.id
  assert data['user']['username'] == user.username
  assert data['user']['email_address'] == user.email_address

def test_get_profile_no_token(client):
  """
  異常系: JWTトークンなしでアクセスした場合に401エラーが返ることをテスト
  """
  response = client.get('/api/v1/profile')
  data = response.get_json()

  assert response.status_code == 401
  # flask_jwt_extendedのデフォルトメッセージ
  assert data['msg'] == 'Missing Authorization Header'

def test_get_profile_invalid_token(client):
  """
  異常系: 無効なJWTトークンでアクセスした場合に422エラーが返ることをテスト
  """
  headers = {
    'Authorization': 'Bearer invalidtoken'
  }
  response = client.get('/api/v1/profile', headers=headers)
  data = response.get_json()

  # flask_jwt_extendedはフォーマットが不正なトークンに対して422を返す
  assert response.status_code == 422
  assert data['msg'] == 'Not enough segments'

def test_get_profile_user_not_found(client):
  """
  異常系: トークンは有効だが、対応するユーザーがDBに存在しない場合に404エラーが返ることをテスト
  """
  with client.application.app_context():
    # 1. テスト用のユーザーを作成し、IDを控える
    user = create_test_user(username="tempuser", email="temp@example.com")
    user_id = user.id
    # 2. アクセストークンを生成
    access_token = create_access_token(identity=str(user_id))
    # 3. ユーザーをDBから削除
    db.session.delete(user)
    db.session.commit()

  # 4. 削除されたユーザーのトークンでAPIにリクエスト
  headers = {'Authorization': f'Bearer {access_token}'}
  response = client.get('/api/v1/profile', headers=headers)
  data = response.get_json()

  # 5. レスポンスを検証
  assert response.status_code == 404
  assert data['message'] == 'ユーザーが見つかりません'