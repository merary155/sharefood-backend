from .helpers import create_test_user
import json

# テストクラス
class TestLoginRoute:
    def test_login_success(self, client):
        """ログインが成功することを確認"""
        with client.application.app_context():
            create_test_user(email="test@example.com", password="testpassword", is_verified=True)

        response = client.post(
            '/api/v1/login',
            data=json.dumps({
                'email_address': 'test@example.com',
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
        with client.application.app_context():
            create_test_user(email="test@example.com", password="testpassword", is_verified=True)

        response = client.post(
            '/api/v1/login',
            data=json.dumps({
                'email_address': 'test@example.com',
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
                'email_address': 'nonexistent@example.com',
                'password': 'anypassword'
            }),
            content_type='application/json'
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data['message'] == 'メールアドレスまたはパスワードが正しくありません'

    def test_login_user_not_verified(self, client):
        """メール未認証のユーザーでログインが失敗することを確認 (403 Forbidden)"""
        with client.application.app_context():
            create_test_user(
                email="unverified@example.com",
                password="password123",
                is_verified=False
            )

        response = client.post(
            '/api/v1/login',
            data=json.dumps({'email_address': 'unverified@example.com', 'password': 'password123'}),
            content_type='application/json'
        )
        assert response.status_code == 403
        assert 'メールアドレスが認証されていません' in response.get_json()['message']

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
        assert 'email_address' in data['errors']

        # emailが不正な形式の場合
        response = client.post(
            '/api/v1/login',
            data=json.dumps({
                'email_address': 'invalid-email-format',
                'password': 'testpassword'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['message'] == '入力データが無効です'
        assert 'email_address' in data['errors']
