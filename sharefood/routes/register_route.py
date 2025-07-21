from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from ..models import User
from .. import db
from sqlalchemy.exc import IntegrityError
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
  schema = RegisterSchema()
  try:
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "リクエストボディにJSONデータがありません"}), 400

    validated_data = schema.load(json_data)

    # メールアドレスが既にデータベースに存在するかチェック
    if User.query.filter_by(email_address=validated_data['email_address']).first():
      return jsonify({'message': 'このメールアドレスは既に使用されています'}), 409

    # 新しいユーザーのインスタンスを作成
    new_user = User(
      username=validated_data['username'],
      email_address=validated_data['email_address']
    )
    new_user.password = validated_data['password']

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'ユーザーが正常に作成されました'}), 201

  except ValidationError as err:
    return jsonify({'message': '入力データが無効です', 'errors': err.messages}), 400
  except IntegrityError:
    db.session.rollback()
    return jsonify({'message': 'このメールアドレスは既に使用されています'}), 409
  except Exception as e:
    db.session.rollback()
    current_app.logger.error(f"登録中に予期せぬエラーが発生: {e}", exc_info=True)
    return jsonify({'message': 'サーバー内部でエラーが発生しました。'}), 500