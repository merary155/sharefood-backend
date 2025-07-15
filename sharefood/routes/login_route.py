from flask import Blueprint, jsonify, request
from ..schemas import LoginSchema, user_schema
from ..models import User
from .. import bcrypt
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token

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
  
  user = User.query.filter_by(email_address=validated_data['email']).first()
  # ユーザーが存在しない、または関数'user.check_password'を起動してハッシュ化パスワードが一致しない場合
  if not user or not user.check_password(validated_data['password']):
    return jsonify({'message': 'メールアドレスまたはパスワードが正しくありません'}), 401
  
  # JWTトークンを生成
  access_token = create_access_token(identity=user.id)
  return jsonify({
    'message': 'ログインに成功しました',
    'access_token': access_token,
    'user': user_schema.dump(user) # user_schema = UserSchema()をschemas.pyで設定、dump()でオブジェクトを辞書に変換
  }), 200

