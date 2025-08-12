import pytest
from flask import jsonify
from sharefood import create_app, db
from sharefood.config import TestingConfig

@pytest.fixture(scope='function')
def client():
  """テスト用のクライアントとクリーンなDBをセットアップするフィクスチャ"""
  app = create_app(config_class=TestingConfig)

  # 404エラーでHTMLが返ってきてたのでJSONで返るようにハンドラを設定
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