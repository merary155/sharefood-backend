from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User
from ..schemas import user_schema

bp = Blueprint('profile_route', __name__, url_prefix='/api/v1')

@bp.route('/profile', methods=['GET'])
@jwt_required() # ログインしている（有効なトークンを持っている）ユーザーのみアクセス可能
def profile():
  current_user_id = int(get_jwt_identity())
  user = User.query.get_or_404(current_user_id, description='ユーザーが見つかりません')
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