import pytest
import json
from sharefood import db
from sharefood.models import Item, User

class TestItemRoute:
  def test_create_item_success(self, client, auth_header):
    """正常に食品を出品できること"""
    payload = {
      "name": "リンゴ",
      "quantity": 10,
      "description": "新鮮なリンゴです",
      "unit": "個"
    }
    response = client.post(
      '/api/v1/items/',
      json=payload,
      headers=auth_header
    )
    data = response.get_json()
    assert response.status_code == 201
    assert data['message'] == '食品が正常に出品されました'
    assert data['item']['name'] == "リンゴ"
    assert data['item']['quantity'] == 10
    assert data['item']['description'] == "新鮮なリンゴです"

    # データベースに正しく保存されたかを確認
    with client.application.app_context():
      user = User.query.filter_by(email_address="test@example.com").first()
      item = Item.query.filter_by(name="リンゴ").first()
      assert item is not None
      assert item.user_id == user.id

  def test_create_item_missing_required(self, client, auth_header):
    """必須フィールドnameやquantityがない場合にエラーとなること"""
    payload = {
      "description": "説明だけ"
    }
    response = client.post(
      '/api/v1/items/',
      json=payload,
      headers=auth_header
    )
    data = response.get_json()
    assert response.status_code == 422
    assert '入力データが無効です' in data['message']
    assert 'name' in data['errors']
    assert 'quantity' in data['errors']

  def test_create_item_unauthorized(self, client):
    """認証なしで出品APIにアクセスしたら401になること"""
    payload = {
      "name": "リンゴ",
      "quantity": 5
    }
    response = client.post(
      '/api/v1/items/',
      json=payload
    )
    assert response.status_code == 401

  def test_get_items(self, client, auth_header):
    """出品されている食品の一覧を取得できること"""
    # まずデータベースに複数商品を追加
    with client.application.app_context():
      user = User.query.first()
      item1 = Item(name="バナナ", quantity=3, user_id=user.id)
      item2 = Item(name="みかん", quantity=5, user_id=user.id)
      db.session.add_all([item1, item2])
      db.session.commit()

    response = client.get('/api/v1/items/')
    data = response.get_json()
    assert response.status_code == 200
    assert isinstance(data['items'], list)
    names = [item['name'] for item in data['items']]
    assert "バナナ" in names
    assert "みかん" in names
    
  # quantityが0以下の場合のテスト
  def test_create_item_invalid_quantity(self, client, auth_header):
      """quantityが0以下の場合にバリデーションエラーとなること"""
      payload = {
        "name": "Zero Quantity Item",
        "description": "Quantity is zero",
        "quantity": 0
      }
      response = client.post('/api/v1/items/', json=payload, headers=auth_header)
      data = response.get_json()
      assert response.status_code == 422
      assert "quantity" in data["errors"]
      assert "数量は1以上で入力してください。" in data["errors"]["quantity"]

  # nameが空文字の場合のテスト
  def test_create_item_empty_name(self, client, auth_header):
      """nameが空文字の場合にバリデーションエラーとなること"""
      payload = {
        "name": "",
        "description": "No name",
        "quantity": 5
      }
      response = client.post('/api/v1/items/', json=payload, headers=auth_header)
      data = response.get_json()
      assert response.status_code == 422
      assert "name" in data["errors"]
      assert "食品名は1文字以上50文字以下で入力してください。" in data["errors"]["name"]

  # descriptionが未入力の場合のテスト（任意フィールドなら成功を想定）
  def test_create_item_without_description(self, client, auth_header):
      """descriptionが任意項目であり、未入力でも成功すること"""
      payload = {
        "name": "No Description",
        "quantity": 10
      }
      response = client.post('/api/v1/items/', json=payload, headers=auth_header)
      data = response.get_json()
      assert response.status_code == 201
      assert "item" in data
      assert data["item"]["description"] is None
