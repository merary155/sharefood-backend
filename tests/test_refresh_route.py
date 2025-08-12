from flask_jwt_extended import create_refresh_token
from .helpers import create_test_user

# ----------------------------------------------
#      <<-- テストの要件 -->>

# リフレッシュトークンを利用してアクセストークンが発行されるか
# トークン無しだと拒否されるか
# 無効なトークンだと拒否されるか
# ----------------------------------------------

def test_refresh_success(client):
  """正常系: 有効なリフレッシュトークンで新しいアクセストークンが取得できることをテスト"""
  with client.application.app_context():
    # テスト用のユーザーを作成し、そのユーザーのリフレッシュトークンを生成
    user = create_test_user()
    refresh_token = create_refresh_token(identity=str(user.id))

  response = client.post('/api/v1/refresh', headers={'Authorization': f'Bearer {refresh_token}'})
  # client.post(...) は テスト用の仮想ブラウザから、/api/v1/refresh にPOSTリクエストを送る
  # headers={'Authorization': f'Bearer{refresh_token}'} は HTTPリクエストヘッダーに「Authorization: Bearer <トークン>」を付ける
  # そのリクエストの「レスポンス（返ってきた結果）」が response 変数に入っている
  
  assert response.status_code == 200
  json_data = response.get_json()     # responseをPythonの辞書やリスト形式に変換して取得
  assert 'access_token' in json_data  

def test_refresh_without_token(client):
  """異常系: トークンなしでアクセスした場合に401エラーが返ることをテスト"""
  response = client.post('/api/v1/refresh')
  data = response.get_json()
  assert response.status_code == 401
  # __init__.py で設定したカスタムエラーメッセージを検証
  assert data['message'] == 'リクエストには認証トークンが必要です'

def test_refresh_with_invalid_token(client):
  """異常系: 無効なトークンでアクセスした場合に422エラーが返ることをテスト"""
  response = client.post(
    '/api/v1/refresh',
    headers={'Authorization': 'Bearer invalid.token.here'}
  )
  data = response.get_json()
  assert response.status_code == 422
  assert data['message'] == '無効な認証トークンです'