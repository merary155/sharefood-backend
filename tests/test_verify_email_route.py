import pytest
from datetime import datetime, timedelta, timezone
from sharefood.models import User # Userモデルをインポート
from sharefood import db # dbインスタンスをインポート

# 既存のヘルパー関数をインポート
# helpers.py にこれらの関数があることを想定
from .helpers import create_test_user, create_test_item, get_auth_header 

# ----------------------------------------------
#      <<-- テストの要件 -->>

# 認証が成功するか
# トークン無しだと拒否されるか
# 無効なトークンだと拒否されるか
# 期限切れトークンだと拒否されるか
# 既に認証済みのユーザーが再度認証リクエストを送信した場合
# ----------------------------------------------

def test_verify_email_success(client):
  """正常系: メール認証が成功するか"""
  with client.application.app_context():
    user = create_test_user(email="unverified_success@example.com", is_verified=False)
    user.generate_verification_token()

    db.session.add(user) # 変更を追跡させる
    db.session.commit()  # トークンと期限の変更をDBに反映
    
    verification_token = user.verification_token

    # メール認証APIにトークンを渡してアクセス
    # その後取得した"HTTPレスポンス"を変数に代入
    response = client.get(f'/api/v1/verify-email?token={verification_token}') 

    data = response.get_json()

    assert response.status_code == 200 # "response.status_code"で、HTTPレスポンススのステータスコードを取得
    assert data['message'] == 'メールアドレスが正常に認証されました。'

    # データベースからユーザーを再取得し、状態が更新されていることを確認
    db.session.refresh(user) # userオブジェクトをDBの最新状態に更新

    # is_verified が True になっていることを確認
    assert user.is_verified is True
    # verification_token が None にクリアされていることを確認
    assert user.verification_token is None
    # token_expires_at が None にクリアされていることを確認
    assert user.token_expires_at is None

def test_verify_email_no_token(client):
  """異常系: トークン無しアクセスは拒否されるか"""
  
  response = client.get('/api/v1/verify-email')
  data = response.get_json()
  
  assert response.status_code == 400
  assert data['message'] == '認証トークンが指定されていません。'

def test_verify_email_invalid_token(client):
  """異常系: 無効なトークンでアクセスは拒否されるか"""
  
  invalid_token = "this_is_an_invalid_token"
  
  response = client.get(f'/api/v1/verify-email?token={invalid_token}')
  data = response.get_json()
  
  assert response.status_code == 404
  assert data['message'] == '無効な認証トークンです。'
  
def test_verify_email_expired_token(client):
  """異常系: 期限切れトークンでのアクセスは拒否されるか"""
  
  with client.application.app_context():
    # ヘルパーを使って未認証ユーザーを作成
    user = create_test_user(email="expired@example.com", is_verified=False)
    
    # 有効期限を1日前（＝期限切れ）に設定
    user.generate_verification_token()
    user.token_expires_at = datetime.now(timezone.utc) - timedelta(days=1)    
    
    db.session.add(user)
    db.session.commit()
    # トークンを取得
    expired_token = user.verification_token

    # トークンを使ってメール認証APIにアクセス
    response = client.get(f'/api/v1/verify-email?token={expired_token}')
    data = response.get_json()

    # レスポンスの確認
    assert response.status_code == 400  # エラーコードが400（Bad Request）になるはず
    assert data['message'] == '認証トークンの有効期限が切れています。'

def test_verify_email_already_verified_user(client):
  """異常系: 既に認証済みのユーザーが再度認証リクエストを送った場合"""

  with client.application.app_context():
    # すでに認証済みのユーザーを作成（is_verified=True）
    user = create_test_user(email="already_verified@example.com", is_verified=True)
    user.generate_verification_token() 

    db.session.add(user)
    db.session.commit()

    token = user.verification_token

    # メール認証APIに再アクセス
    response = client.get(f'/api/v1/verify-email?token={token}')
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'すでに認証済みのユーザーです。'
