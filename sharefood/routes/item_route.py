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

# --- アイテムを1件のみ詳細取得 ---
@bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
  item = Item.query.get_or_404(item_id)
  return jsonify({'item': item_schema.dump(item)}), 200

# --- アイテム一覧表示・絞り込み機能 ---
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

# --- アイテム編集 ---
@bp.route('/<int:item_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_item(item_id): # この引数はURLから取得される
  item = Item.query.get_or_404(item_id)
  current_user_id = get_jwt_identity()
  if item.user_id != current_user_id:
    return jsonify({'message': '権限がありません'}), 403

  try:
    validated_data = item_schema.load(request.get_json(), partial=True)
  except ValidationError as err:
    return jsonify({'message': '入力データが無効です', 'errors': err.messages}), 400

  for key, value in validated_data.items():
    setattr(item, key, value)

  db.session.commit()
  return jsonify({'message': '食品情報を更新しました', 'item': item_schema.dump(item)}), 200

# --- アイテム削除 ---
@bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id): # この引数はURLから取得される
  item = Item.query.get_or_404(item_id)
  current_user_id = get_jwt_identity()
  if item.user_id != current_user_id:
    return jsonify({'message': '権限がありません'}), 403

  db.session.delete(item)
  db.session.commit()
  return jsonify({'message': '食品を削除しました'}), 200

# --- アイテム画像アップロード ---
@bp.route('/<int:item_id>/image', methods=['POST'])
@jwt_required()
def upload_item_image(item_id): # この引数はURLから取得される
  item = Item.query.get_or_404(item_id)
  current_user_id = get_jwt_identity()
  if item.user_id != current_user_id:
    return jsonify({'message': '権限がありません'}), 403

  if 'image' not in request.files:
    return jsonify({'message': '画像ファイルがありません'}), 400

  image = request.files['image']
  if image.filename == '':
    return jsonify({'message': 'ファイル名がありません'}), 400

  # 画像保存処理（例: staticディレクトリに保存）
  import os
  from werkzeug.utils import secure_filename

  filename = secure_filename(image.filename)
  save_dir = os.path.join('static', 'item_images')
  os.makedirs(save_dir, exist_ok=True)
  save_path = os.path.join(save_dir, filename)
  image.save(save_path)

  # アイテムに画像パスを保存（models.pyにimage_pathカラムが必要）
  item.image_path = save_path
  db.session.commit()

  return jsonify({'message': '画像をアップロードしました', 'image_path': save_path}), 200