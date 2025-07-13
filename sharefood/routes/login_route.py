from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required
from ..models import User
from .. import db, bcrypt

bp = Blueprint('login_route', __name__, url_prefix='/api/v1')

@bp.route('/login', methods=['POST'])
def login():
  data = request.get_json()
  # 3つの条件のうちどれか1つでも当てはまれば return される
  if not data or 'email' not in data or 'password' not in data:
    return jsonify({'message': 'メールアドレスとパスワードは必須です'}), 400
  
  user = User.query.filter_by(email_address=data['email']).first()
  # ユーザーが存在しない、または関数'user.check_password'を起動してハッシュ化パスワードが一致しない場合
  if not user or not user.check_password(data['password']):
    return jsonify({'message': 'メールアドレスまたはパスワードが正しくありません'}), 401
  
  login_user(user)
  return jsonify({
    'message': 'ログインに成功しました',
    'user': {
      'id': user.id,
      'username': user.username,
      'email': user.email_address
    }
  }), 200

# JWT追加予定