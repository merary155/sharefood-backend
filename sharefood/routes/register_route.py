from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from ..models import User
from .. import db
from ..schemas import RegisterSchema

# Blueprintを作成
# 'api'はBlueprintの名前、__name__は現在のモジュール名、url_prefixでURLの先頭に/api/v1を付与
bp = Blueprint('register_route', __name__, url_prefix='/api/v1')

@bp.route('/status')
def status():
  response_data = {'status': 'ok', 'message': 'Backend is running!'}
  return jsonify(response_data)

# ユーザー登録API
@bp.route('/register', methods=['POST'])
def register():
  # ここでmarshmallowのSchemaを使用
  schema = RegisterSchema()
  try:
    # request.get_json() で取得したデータをschema.load() に渡す
    # バリデーションに成功すると、validated_dataが返される
    validated_data = schema.load(request.get_json())
  except ValidationError as err:
    # バリデーションエラーが発生した場合
    return jsonify({'message': '入力データが無効です', 'errors': err.messages}), 400

  # メールアドレスが既にデータベースに存在するかチェック
  # validated_data['email_address'] を使用
  if User.query.filter_by(email_address=validated_data['email_address']).first():
    return jsonify({'message': 'このメールアドレスは既に使用されています'}), 409

  # 新しいユーザーのインスタンスを作成
  # validated_data['username'], validated_data['email_address'] を使用
  new_user = User(
      username=validated_data['username'],
      email_address=validated_data['email_address']
  )
  # models.pyで定義したセッター(@password.setter)により、
  # パスワードは自動的にハッシュ化されて保存される
  # validated_data['password'] を使用
  new_user.password = validated_data['password']

  # データベースセッションに新しいユーザーを追加して、変更をコミット（保存）
  db.session.add(new_user)
  db.session.commit()

  return jsonify({'message': 'ユーザーが正常に作成されました'}), 201