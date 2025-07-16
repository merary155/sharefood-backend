import pytest
import json
from sharefood import create_app, db, bcrypt # __init__.py から create_app をインポート
from sharefood.models import User # Userモデルをインポート
from sharefood.config import TestingConfig # テスト用の設定クラスをインポート

# pytestのフィクスチャを使って、テストクライアントとDBのセットアップ・ティアダウンを自動化
@pytest.fixture
def client():
    # テスト設定でFlaskアプリケーションを作成
    app = create_app(TestingConfig) 
    # Flaskインスタンスの test_client() を with で使ってテスト用クライアントを取得、as + 変数
    with app.test_client() as client:
        # アプリケーションコンテキスト内でDBを初期化
        with app.app_context():
            db.create_all() # テーブルを作成

            # テストユーザーを事前に作成
            hashed_password = bcrypt.generate_password_hash("testpassword").decode('utf-8')
            test_user = User(email_address="test@example.com", password=hashed_password)
            db.session.add(test_user)
            db.session.commit()
        yield client # テスト関数にクライアントを渡す
        # テスト終了後にDBをクリーンアップ
        with app.app_context():
            db.session.remove()
            db.drop_all() # テーブルを削除

# テストクラス
class TestLoginRoute:
    def test_login_success(self, client):
        """ログインが成功することを確認"""
        response = client.post(
            '/api/v1/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'testpassword'
            }),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert data['message'] == 'ログインに成功しました'
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['email_address'] == 'test@example.com'

    def test_login_invalid_credentials(self, client):
        """不正な認証情報でログインが失敗することを確認"""
        response = client.post(
            '/api/v1/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data['message'] == 'メールアドレスまたはパスワードが正しくありません'

    def test_login_user_not_found(self, client):
        """存在しないユーザーでログインが失敗することを確認"""
        response = client.post(
            '/api/v1/login',
            data=json.dumps({
                'email': 'nonexistent@example.com',
                'password': 'anypassword'
            }),
            content_type='application/json'
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data['message'] == 'メールアドレスまたはパスワードが正しくありません'

    def test_login_invalid_input_data(self, client):
        """入力データが無効な場合にエラーとなることを確認"""
        # emailフィールドがない場合
        response = client.post(
            '/api/v1/login',
            data=json.dumps({
                'password': 'testpassword'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['message'] == '入力データが無効です'
        assert 'email' in data['errors']

        # emailが不正な形式の場合
        response = client.post(
            '/api/v1/login',
            data=json.dumps({
                'email': 'invalid-email-format',
                'password': 'testpassword'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['message'] == '入力データが無効です'
        assert 'email' in data['errors']


