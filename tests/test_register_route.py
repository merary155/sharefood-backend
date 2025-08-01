import pytest
import json
from sharefood import db
from sharefood.models import User

class TestRegisterRoute:
    """/api/v1/register エンドポイントのテストスイート"""

    def test_register_success(self, client):
        """正常なデータでユーザー登録が成功することを確認 (201 Created)"""
        response = client.post(
            '/api/v1/register',
            data=json.dumps({
                'username': 'newuser',
                'email_address': 'new@example.com',
                'password': 'Password123'
            }),
            content_type='application/json'
        )
        data = response.get_json()

        assert response.status_code == 201
        assert data['message'] == 'ユーザーが正常に作成されました'

        # データベースにユーザーが正しく作成されたか確認
        user = User.query.filter_by(email_address='new@example.com').first()
        assert user is not None
        assert user.username == 'newuser'
        assert user.check_password('Password123')

    def test_register_email_conflict(self, client):
        """既に存在するメールアドレスでの登録が失敗することを確認 (409 Conflict)"""
        # 事前に同じメールアドレスのユーザーを作成
        with client.application.app_context():
            existing_user = User(username='testuser', email_address='test@example.com')
            existing_user.password = 'Password123'
            db.session.add(existing_user)
            db.session.commit()
        
        # 同じメールアドレスで登録を試みる
        response = client.post(
            '/api/v1/register',
            data=json.dumps({
                'username': 'anotheruser',
                'email_address': 'test@example.com', # 既存のメールアドレス
                'password': 'AnotherPassword123'
            }),
            content_type='application/json'
        )
        data = response.get_json()
        assert response.status_code == 409
        assert data['message'] == 'このメールアドレスは既に使用されています'

    @pytest.mark.parametrize("payload, error_field, error_message", [
        # --- 必須フィールド欠落 ---
        ({"email_address": "a@b.com", "password": "Password123"}, "username", "Missing data for required field."),
        ({"username": "test", "password": "Password123"}, "email_address", "Missing data for required field."),
        ({"username": "test", "email_address": "a@b.com"}, "password", "Missing data for required field."),
        
        # --- 空の文字列やフォーマット違反 ---
        ({"username": "", "email_address": "a@b.com", "password": "Password123"}, "username", "ユーザー名は必須です。"),
        ({"username": "test", "email_address": "invalid-email", "password": "Password123"}, "email_address", "有効なメールアドレスを入力してください。"),
        
        # --- パスワード強度違反 ---
        ({"username": "test", "email_address": "a@b.com", "password": "short"}, "password", "パスワードは8文字以上で入力してください。"),
        ({"username": "test", "email_address": "a@b.com", "password": "password123"}, "password", "パスワードには少なくとも1つの大文字が必要です。"),
        ({"username": "test", "email_address": "a@b.com", "password": "PASSWORD123"}, "password", "パスワードには少なくとも1つの小文字が必要です。"),
        ({"username": "test", "email_address": "a@b.com", "password": "PasswordAbc"}, "password", "パスワードには少なくとも1つの数字が必要です。"),
    ])
    def test_register_invalid_input(self, client, payload, error_field, error_message):
        """不正な入力データで登録が失敗することを確認 (400 Bad Request)"""
        response = client.post(
            '/api/v1/register',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data['message'] == '入力データが無効です'
        assert error_field in data['errors']
        assert error_message in data['errors'][error_field]

    def test_status_endpoint(self, client):
        """/status エンドポイントが正常に動作することを確認 (200 OK)"""
        response = client.get('/api/v1/status')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['message'] == 'Backend is running!'