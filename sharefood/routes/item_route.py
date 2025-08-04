import os
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import Item
from ..schemas import item_schema, items_schema

bp = Blueprint('item_route', __name__, url_prefix='/api/v1/items')

@bp.route('/', methods=['POST'])
@jwt_required()
def create_item():
  # multipart/form-data からテキストデータを取得
  data = request.form.to_dict()
 
  try:
    validated_data = item_schema.load(data)
  except ValidationError as err:
    return jsonify({'message': '入力データが無効です', 'errors': err.messages}), 422
  
  current_user_id = int(get_jwt_identity())
  validated_data['user_id'] = current_user_id
  new_item = Item(**validated_data)
  
  # 画像ファイルの処理
  # フロントエンドからは 'image' というキーでファイルを送信することを想定
  if 'image' in request.files:
    file = request.files['image']
    # ファイルが存在し、ファイル名が空でないことを確認
    if file and file.filename != '':
      filename = secure_filename(file.filename)
      save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
      file.save(save_path)
      new_item.img_url = filename # ファイル名をDBに保存

  db.session.add(new_item)
  db.session.commit()
  
  return jsonify({'message': '食品が正常に出品されました', 'item': item_schema.dump(new_item)}), 201
  
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
  
  current_user_id = int(get_jwt_identity())
  
  if item.user_id != current_user_id:
    return jsonify({'message': '権限がありません'}), 403

  try:
    validated_data = item_schema.load(request.get_json(), partial=True)
  except ValidationError as err:
    return jsonify({'message': '入力データが無効です', 'errors': err.messages}), 422

  for key, value in validated_data.items():
    setattr(item, key, value)

  db.session.commit()
  return jsonify({'message': '食品情報を更新しました', 'item': item_schema.dump(item)}), 200

# --- アイテム削除 ---
@bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id): # この引数はURLから取得される
  item = Item.query.get_or_404(item_id)

  current_user_id = int(get_jwt_identity())
  
  if item.user_id != current_user_id:
    return jsonify({'message': '権限がありません'}), 403

  db.session.delete(item)
  db.session.commit()
  return jsonify({'message': '食品を削除しました'}), 200
