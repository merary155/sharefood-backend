import pytest
from sharefood import create_app, db
from sharefood.models import User
from sharefood.config import TestingConfig
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='module')
def client():
  """テスト用のクライアントとクリーンなDBをセットアップするフィクスチャ"""
  app = create_app(config_class=TestingConfig)
  with app.test_client() as client:
    with app.app_context():
      db.create_all()
    yield client
    with app.app_context():
      db.session.remove()
      db.drop_all()

@pytest.fixture(scope='module')
def auth_header(client):
  """テスト用のユーザー作成とアクセストークンを発行するフィクスチャ"""
  with client.application.app_context():
    user = User(username="testuser", email_address="test@example.com")
    user.password = "Password123"
    db.session.add(user)
    db.session.commit()
    access_token = create_access_token(identity=user.id)
    return {"Authorization": f"Bearer {access_token}"}