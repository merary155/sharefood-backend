import pytest
from flask import jsonify
from sharefood import create_app, db, bcrypt
from sharefood.models import User
from sharefood.config import TestingConfig
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='function')
def client():
  """テスト用のクライアントとクリーンなDBをセットアップするフィクスチャ"""
  app = create_app(config_class=TestingConfig)

  # 404エラーがJSONで返るようにハンドラを設定
  @app.errorhandler(404)
  def not_found_error(error):
      return jsonify({"message": error.description or "Not Found"}), 404

  with app.test_client() as client:
    with app.app_context():
      db.create_all()
    yield client
    with app.app_context():
      db.session.remove()
      db.drop_all()

@pytest.fixture(scope='function')
def auth_header(client):
  """テスト用のユーザー作成とアクセストークンを発行するフィクスチャ"""
  with client.application.app_context():
    user = User(username="testuser", email_address="test@example.com", password_hash=bcrypt.generate_password_hash("Password123").decode('utf-8'))
    db.session.add(user)
    db.session.commit()
    access_token = create_access_token(identity=str(user.id))
    return {"Authorization": f"Bearer {access_token}"}