from flask import Blueprint, jsonify, request
# 今後の実装で必要になるもの
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_jwt_extended import create_access_token
from ..models import User
from .. import db

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
  data = request.get_json() # フロントエンドから送信されたJSONデータを取得
  # 必須項目がJSONデータに含まれているか簡単なチェック
  if not data or not 'username' in data or not 'email' in data or not 'password' in data:
  # 項目が不足している場合は、400 Bad Requestエラーを返します
    return jsonify({'message': '必須項目が不足しています'}), 400
  
  # メールアドレスが既にデータベースに存在するかチェック
  if User.query.filter_by(email_address=data['email']).first():
    # 存在する場合は、409 Conflictエラーを返します
    return jsonify({'message': 'このメールアドレスは既に使用されています'}), 409

  # 新しいユーザーのインスタンスを作成
  new_user = User(
      username=data['username'],
      email_address=data['email']
  )
  # models.pyで定義したセッター(@password.setter)により、
  # パスワードは自動的にハッシュ化されて保存される
  new_user.password = data['password']

  # データベースセッションに新しいユーザーを追加して、変更をコミット（保存）
  db.session.add(new_user)
  db.session.commit()

  # 成功メッセージとステータスコード201 Createdを返します
  return jsonify({'message': 'ユーザーが正常に作成されました'}), 201