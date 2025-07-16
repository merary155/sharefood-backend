import pytest
from sharefood import create_app
from sharefood.models import db


@pytest.fixture(scope='module')
def test_app():
    """テスト用のFlaskアプリケーションインスタンスを作成するフィクスチャ"""
    # "testing"モードでアプリケーションを作成
    app = create_app(testing=True)

    with app.app_context():
        # テスト用のインメモリSQLiteデータベースを使用
        db.create_all()
        yield app  # テストの実行
        db.drop_all()


@pytest.fixture(scope='module')
def test_client(test_app):
    """テスト用のクライアントを作成するフィクスチャ"""
    return test_app.test_client()