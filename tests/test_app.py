def test_app_creation(test_client):
    """アプリケーションが正常に作成されることをテスト"""
    assert test_client.application is not None

def test_hello_world(test_client):
    """(例) Hello Worldエンドポイントのテスト"""
    # response = test_client.get('/')
    # assert response.status_code == 200
    # assert b"Hello, World!" in response.data
    pass  # まだエンドポイントがないので一旦pass