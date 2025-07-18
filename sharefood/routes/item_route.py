from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

from .. import db
from ..models import Item
from ..schemas import item_schema, items_schema

bp = Blueprint('item_route', __name__, url_prefix='/api/v1/items')

# --- 食品を出品（登録）API ---
@bp.route('/', methods=['POST'])
@jwt_required()
def create_item():
  try:
    # このURLで受け取ったjsonデータをPythonの辞書に変換→それをschema.load()でバリデーション・整形
    validated_data = item_schema.load(request.get_json())
  except ValidationError as err:
    return jsonify({'message': '入力データが無効です', 'errors': err.messages}), 400

  # 現在ログインしているユーザーのIDを取得
  current_user_id = get_jwt_identity()

  # 新しいItemオブジェクトを作成
  new_item = Item(
    name = validated_data['name'],
    quantity = validated_data['quantity'],
    user_id = current_user_id
  )

  # オプショナルなフィールドを一つずつチェックして追加
  if 'description' in validated_data:
    new_item.description = validated_data['description']
  if 'unit' in validated_data:
    new_item.unit = validated_data['unit']
  if 'expiration_date' in validated_data:
    new_item.expiration_date = validated_data['expiration_date']
  if 'location' in validated_data:
    new_item.location = validated_data['location']

  db.session.add(new_item)
  db.session.commit()

  return jsonify({'message': '商品が正常に出品されました', 'item': item_schema.dump(new_item)}), 201

@bp.route('/', methods=['GET'])
def get_items():
  query = Item.query

  # 絞り込み条件をクエリパラメータから取得
  name = request.args.get('name')
  is_available = request.args.get('is_available')

  if name:
    query = query.filter(Item.name.ilike(f'%{name}%'))
  if is_available is not None:
    if is_available.lower() == 'true':
      query = query.filter(Item.is_available.is_(True))
    elif is_available.lower() == 'false':
      query = query.filter(Item.is_available.is_(False))

  items = query.order_by(Item.created_at.desc()).all()

  return jsonify({'items': items_schema.dump(items)}), 200
