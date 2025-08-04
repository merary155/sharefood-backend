from sharefood import db
from sharefood.models import User, Item
from flask_jwt_extended import create_access_token

def create_test_user(username="testuser", email="test@example.com", password="password", is_verified=True):
  """テスト用のユーザーをDBに作成するヘルパー関数"""
  user = User(username=username, email_address=email, is_verified=is_verified)
  user.password = password
  db.session.add(user)
  db.session.commit()
  return user

def create_test_item(user, name="テスト商品", description="テスト説明", quantity=5):
  """テスト用のアイテムをDBに作成するヘルパー関数"""
  item = Item(name=name, description=description, quantity=quantity, user_id=user.id)
  db.session.add(item)
  db.session.commit()
  return item

def get_auth_header(user_id):
  """指定されたユーザーIDで認証ヘッダーを生成するヘルパー関数"""
  access_token = create_access_token(identity=str(user_id))
  return {"Authorization": f"Bearer {access_token}"}