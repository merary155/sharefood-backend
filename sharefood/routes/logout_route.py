from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

bp = Blueprint('logout_route', __name__, url_prefix='/api/v1')

# ユーザーログアウトAPI
@bp.route('/logout', methods=['POST'])
@jwt_required() # ログインしている（有効なトークンを持っている）ユーザーのみアクセス可能
def logout():
  return jsonify({'message': 'ログアウトに成功しました'}), 200

# 実際はReact側でJWTトークンを削除するコードを書くことによってログアウトが完了する