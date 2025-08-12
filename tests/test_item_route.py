from sharefood import db
from .helpers import create_test_user, get_auth_header, create_test_item
from sharefood.models import Item

# --- POST /items のテスト ---
class TestItemRoute:

  def test_create_item_success(self, client):
    with client.application.app_context():
      user = create_test_user()
      auth_header = get_auth_header(user.id)

    payload = {
      "name": "リンゴ",
      "quantity": 10,
      "description": "新鮮なリンゴです",
      "unit": "個"
    }
    response = client.post('/api/v1/items/', data=payload, headers=auth_header)
    data = response.get_json()

    assert response.status_code == 201
    assert data['message'] == '食品が正常に出品されました'
    assert data['item']['name'] == "リンゴ"

  def test_create_item_missing_required(self, client):
    with client.application.app_context():
      user = create_test_user()
      auth_header = get_auth_header(user.id)

    payload = {"description": "説明だけ"}
    response = client.post('/api/v1/items/', data=payload, headers=auth_header)
    data = response.get_json()

    assert response.status_code == 422
    assert 'name' in data['errors']
    assert 'quantity' in data['errors']

  def test_create_item_unauthorized(self, client):
    payload = {"name": "リンゴ", "quantity": 5}
    response = client.post('/api/v1/items/', data=payload)
    assert response.status_code == 401

  def test_create_item_invalid_quantity(self, client):
    with client.application.app_context():
      user = create_test_user()
      auth_header = get_auth_header(user.id)

    payload = {"name": "Invalid", "quantity": 0}
    response = client.post('/api/v1/items/', data=payload, headers=auth_header)
    data = response.get_json()
    assert response.status_code == 422
    assert "quantity" in data["errors"]

  def test_create_item_empty_name(self, client):
    with client.application.app_context():
      user = create_test_user()
      auth_header = get_auth_header(user.id)

    payload = {"name": "", "quantity": 5}
    response = client.post('/api/v1/items/', data=payload, headers=auth_header)
    data = response.get_json()
    assert response.status_code == 422
    assert "name" in data["errors"]

  def test_create_item_without_description(self, client):
    with client.application.app_context():
      user = create_test_user()
      auth_header = get_auth_header(user.id)

    payload = {"name": "No Desc", "quantity": 10}
    response = client.post('/api/v1/items/', data=payload, headers=auth_header)
    data = response.get_json()
    assert response.status_code == 201
    assert data["item"]["description"] is None


# --- GET /items のテスト ---
def test_get_items(client):
  with client.application.app_context():
    user = create_test_user()
    create_test_item(user, name="バナナ", quantity=3)
    create_test_item(user, name="みかん", quantity=5)

  response = client.get('/api/v1/items/')
  data = response.get_json()
  names = [item['name'] for item in data['items']]
  assert response.status_code == 200
  assert "バナナ" in names
  assert "みかん" in names


# --- PUT /items/<id> のテスト ---
def test_update_item_success(client):
  with client.application.app_context():
    user = create_test_user()
    item = create_test_item(user)
    auth_header = get_auth_header(user.id)
    item_id = item.id

  update_data = {"name": "更新された商品", "description": "説明更新"}
  response = client.put(f'/api/v1/items/{item_id}', json=update_data, headers=auth_header)
  data = response.get_json()
  assert response.status_code == 200
  assert data['item']['name'] == "更新された商品"


def test_update_item_not_owner(client):
  with client.application.app_context():
    owner = create_test_user("owner", "owner@test.com")
    other = create_test_user("other", "other@test.com")
    item = create_test_item(owner)
    auth_header = get_auth_header(other.id)
    item_id = item.id

  update_data = {"name": "悪意ある更新"}
  response = client.put(f'/api/v1/items/{item_id}', json=update_data, headers=auth_header)
  assert response.status_code == 403


def test_update_item_not_found(client):
  with client.application.app_context():
    user = create_test_user()
    auth_header = get_auth_header(user.id)

  response = client.put('/api/v1/items/99999', json={"name": "x"}, headers=auth_header)
  assert response.status_code == 404


# --- DELETE /items/<id> のテスト ---
def test_delete_item_success(client):
  with client.application.app_context():
    user = create_test_user()
    item = create_test_item(user)
    auth_header = get_auth_header(user.id)
    item_id = item.id

  response = client.delete(f'/api/v1/items/{item_id}', headers=auth_header)
  assert response.status_code == 200
  with client.application.app_context():
    assert db.session.get(Item, item_id) is None


def test_delete_item_not_owner(client):
  with client.application.app_context():
    owner = create_test_user("owner", "owner@test.com")
    attacker = create_test_user("hacker", "hacker@test.com")
    item = create_test_item(owner)
    auth_header = get_auth_header(attacker.id)
    item_id = item.id

  response = client.delete(f'/api/v1/items/{item_id}', headers=auth_header)
  assert response.status_code == 403


def test_delete_item_not_found(client):
  with client.application.app_context():
    user = create_test_user()
    auth_header = get_auth_header(user.id)

  response = client.delete('/api/v1/items/99999', headers=auth_header)
  assert response.status_code == 404
