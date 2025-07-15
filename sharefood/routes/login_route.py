from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required
from ..schemas import LoginSchema
from ..models import User
from .. import db, bcrypt

bp = Blueprint('login_route', __name__, url_prefix='/api/v1')

# ユーザログインAPI
@bp.route('/login', methods=['POST'])
def login():
  # ここでmarshmallowのSchemaを使用
  schema = LoginSchema()
  try:
    # request.get_json() で取得したデータをschema.load() に渡す
    # バリデーションに成功すると、validated_dataが返される
    validated_data = schema.load(request.get_json())
  except ValidationError as err:
    # バリデーションエラーが発生した場合
    return jsonify({'message': '入力データが無効です', 'errors': err.messages}), 400
    
  # 3つの条件のうちどれか1つでも当てはまれば return される
  if not validated_data or 'email' not in validated_data or 'password' not in validated_data:
    return jsonify({'message': 'メールアドレスとパスワードは必須です'}), 400
  
  user = User.query.filter_by(email_address=validated_data['email']).first()
  # ユーザーが存在しない、または関数'user.check_password'を起動してハッシュ化パスワードが一致しない場合
  if not user or not user.check_password(validated_data['password']):
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