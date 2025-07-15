from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

from .. import db
from ..models import Item
from ..schemas import item_schema, items_schema

bp = Blueprint('item_route', __name__, url_prefix='/api/v1/items')

# --- 食品を出品（登録）するAPI ---
@bp.route('/', methods=['POST'])
@jwt_required() # ログインが必須
def create_item():
  try:
    # リクエストされたJSONをスキーマでバリデーション・デシリアライズ(dumpがシリアライズ)
    validated_data = item_schema.load(request.get_json())
  except ValidationError as err:
    return jsonify({'message': '入力データが無効です', 'errors': err.messages}), 400

  # 現在ログインしているユーザーのIDを取得
  current_user_id = get_jwt_identity()

  # 新しいItemオブジェクトを作成
  new_item = Item(
      name=validated_data['name'],
      quantity=validated_data['quantity'],
      user_id=current_user_id # 出品者としてログインユーザーのIDを設定
  )
  # オプショナルなフィールドも設定
  if 'description' in validated_data:
    new_item.description = validated_data['description']

  db.session.add(new_item)
  db.session.commit()

  return jsonify({'message': '食品が正常に出品されました', 'item': item_schema.dump(new_item)}), 201

# --- 出品されている食品の一覧を取得するAPI ---
@bp.route('/', methods=['GET'])
def get_items():
  all_items = Item.query.order_by(Item.created_at.desc()).all()
  # items_schema (many=True) を使ってリストをシリアライズ
  return jsonify({'items': items_schema.dump(all_items)}), 200