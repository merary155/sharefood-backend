from flask import Blueprint, jsonify, request
from ..schemas import LoginSchema, user_schema
from ..models import User
from .. import bcrypt
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token

bp = Blueprint('login_route', __name__, url_prefix='/api/v1')

# リアクト側が'/login'にPOSTメソッドでリクエスト送信（そのbodyの中にjson形式のデータがある）
# それをrequest.get_json()で受け取りPythonの辞書に変更→schema.loadでバリデーションチェック→それがvalidated_dataに代入される

# ユーザログインAPI
@bp.route('/login', methods=['POST'])
def login():
  schema = LoginSchema()
  try:
    # LoginSchema()でチェックしたemailとpwをここでPythonの辞書に変更
    validated_data = schema.load(request.get_json())
  except ValidationError as err:
    return jsonify({'message': '入力データが無効です', 'errors': err.messages}), 400

  user = User.query.filter_by(email_address=validated_data['email_address']).first()
  # Userの中にuser(email)があるか、またUserの中にハッシュ化されたPWと一致するかを確認
  if not user or not user.check_password(validated_data['password']):
    return jsonify({'message': 'メールアドレスまたはパスワードが正しくありません'}), 401
  
  # emailとPWに問題なければJWTトークン生成
  access_token = create_access_token(identity=str(user.id))
  return jsonify({
    'message': 'ログインに成功しました',
    'access_token': access_token,
    'user': user_schema.dump(user)
  }), 200