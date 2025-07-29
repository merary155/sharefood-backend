
import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_refresh_token
from sharefood.routes.refresh_route import bp

@pytest.fixture
def app():
  app = Flask(__name__)
  app.config['JWT_SECRET_KEY'] = 'test-secret'
  app.register_blueprint(bp)
  JWTManager(app)
  return app

# テスト用の仮想ユーザー情報を生成
@pytest.fixture
def client(app):
  return app.test_client()

# ----------------------------------------------
#      <<-- テストの要件 -->>

# リフレッシュトークンを利用してアクセストークンが発行されるか
# トークン無しだと拒否されるか
# 無効なトークンだと拒否されるか
# 違ったユーザーIDを入れた場合エラーになるか
# ----------------------------------------------

def test_refresh_success(client):
  # テスト用のユーザーID
  test_user_id = 1
  # リフレッシュトークン発行
  refresh_token = create_refresh_token(identity=test_user_id)
  response = client.post(
    '/api/v1/refresh',
    headers={'Authorization': f'Bearer {refresh_token}'}
  )
  # client.post(...) は テスト用の仮想ブラウザから、/api/v1/refresh にPOSTリクエストを送る
  # headers={'Authorization': f'Bearer{refresh_token}'} は HTTPリクエストヘッダーに「Authorization: Bearer <トークン>」を付ける
  # そのリクエストの「レスポンス（返ってきた結果）」が response 変数に入っている
  
  assert response.status_code == 200
  json_data = response.get_json()     # responseをPythonの辞書やリスト形式に変換して取得
  assert 'access_token' in json_data  

def test_refresh_without_token(client):
  response = client.post('/api/v1/refresh')
  assert response.status_code == 401

def test_refresh_with_invalid_token(client):
  response = client.post(
    '/api/v1/refresh',
    headers={'Authorization': 'Bearer invalid.token.here'}
  )
  assert response.status_code in (401, 422)

def test_refresh_with_invalid_id(client):
  test_invalid_id = 99999
  refresh_token = create_refresh_token(identity=test_invalid_id)
  response = client.post(
    '/api/v1/refresh',
    headers={'Authorization': f'Bearer {refresh_token}'}
  )
  assert response.status_code == 401
  
  