import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from sharefood.routes.logout_route import bp

@pytest.fixture
def app():
  app = Flask(__name__)
  app.config['JWT_SECRET_KEY'] = 'test-secret'
  app.register_blueprint(bp)
  JWTManager(app)
  return app

@pytest.fixture
def client(app):
  return app.test_client()

# ----------------------------------------------
#      <<-- テストの要件 -->>

# 正常にログアウト出来たら200が返ってくるか
# トークン無しだと拒否されるか
# 無効なトークンだと拒否されるか
# 違ったユーザーIDを入れた場合エラーになるか
# ----------------------------------------------
  
def test_logout_success(client):
  test_user_id = 1
  access_token = create_access_token(identity=test_user_id)
  response = client.post(
    '/api/v1/logout',
    headers={'Authorization': f'Bearer {access_token}'}
  )
  assert response.status_code == 200
  data = response.get_json()
  assert data['message'] == 'ログアウトに成功しました'

def test_logout_without_token(client):
  response = client.post('/api/v1/logout')
  assert response.status_code == 401

def test_logout_with_invalid_token(client):
  response = client.post(
    '/api/v1/logout',
    headers={'Authorization': 'Bearer invalid.token.here'}
  )
  assert response.status_code in (401, 422)

def test_logout_with_invalid_id(client):
  test_invalid_user_id = 9999
  invalid_access_token = create_access_token(identity=test_invalid_user_id)
  response = client.post(
    '/api/v1/logout',
    headers={'Authorization': f'Bearer {invalid_access_token}'}
  )
  assert response.status_code == 401