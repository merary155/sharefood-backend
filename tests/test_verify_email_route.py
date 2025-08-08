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

    