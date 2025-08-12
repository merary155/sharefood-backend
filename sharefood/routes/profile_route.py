from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Item
from .. import db
from ..schemas import user_schema, items_schema

bp = Blueprint('profile_route', __name__, url_prefix='/api/v1')

@bp.route('/me', methods=['GET'])
@jwt_required() # ログインしている（有効なトークンを持っている）ユーザーのみアクセス可能
def profile():
  current_user_id = int(get_jwt_identity())
  user = db.get_or_404(User, current_user_id, description='ユーザーが見つかりません')
  # ↑このコードは
  # user = User.query.get(current_user_id)
  # if user is None:
  #   abort(404, description='ユーザーが見つかりません')
  # return user
  # というコードを１行でまとめており、errorが返ってきた時のみdescriptionも実行される
  
  return jsonify({
    'message': 'プロフィールを取得しました',
    'user': user_schema.dump(user)
  }), 200

@bp.route('/my/items', methods=['GET'])
@jwt_required()
def get_my_items():
  """ログイン中のユーザーが登録した食品一覧を取得する"""
  current_user_id = get_jwt_identity()
  # ログインユーザーのIDに紐づくItemを全て取得し、新しい順に並べる
  items = Item.query.filter_by(user_id=current_user_id).order_by(Item.created_at.desc()).all()
  # items_schemaでシリアライズしてJSON配列として返す
  # フロントエンドは FoodItem[] を期待しているため、配列を直接返す
  return jsonify(items_schema.dump(items)), 200