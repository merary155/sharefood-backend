from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from ..models import User
from .. import db, mail
from sqlalchemy.exc import IntegrityError
from ..schemas import RegisterSchema
from flask_mail import Message
import textwrap

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
    existing_user = User.query.filter_by(email_address=validated_data['email_address']).first()
    if existing_user:
      if existing_user.is_verified:
        return jsonify({'message': 'このメールアドレスは既に使用されています'}), 409
      else:
        # 未認証の場合は、既存ユーザー情報を更新し、認証メールを再送
        existing_user.username = validated_data['username'] # 名前も更新したい場合
        existing_user.password = validated_data['password'] # パスワードも更新
        token = existing_user.generate_verification_token() # 新しいトークンを生成
        db.session.commit()
        send_verification_email(existing_user.email_address, token) # 認証メールを再送
        return jsonify({'message': 'このメールアドレスは登録済みですが、認証が完了していません。新しい認証メールを送信しました。'}), 200

    # 新しいユーザーのインスタンスを作成
    new_user = User(
      username=validated_data['username'],
      email_address=validated_data['email_address'],
      is_verified=False
    )
    
    new_user.password = validated_data['password']  # Userのpasswordに、入力されたバリデーション通過済のパスワードをセット

    token = new_user.generate_verification_token()  # メアド認証用のトークン

    db.session.add(new_user)
    db.session.commit()

    send_verification_email(new_user.email_address, token)

    return jsonify({'message': 'ユーザー登録が完了しました。登録されたメールアドレスに送られた認証メールを確認してください。'}), 201

  except ValidationError as err:
    return jsonify({'message': '入力データが無効です', 'errors': err.messages}), 400
  except IntegrityError:
    db.session.rollback()
    return jsonify({'message': 'このメールアドレスは既に使用されています'}), 409
  except Exception as e:
    db.session.rollback()
    current_app.logger.error(f"登録中に予期せぬエラーが発生: {e}", exc_info=True)
    return jsonify({'message': 'サーバー内部でエラーが発生しました。'}), 500

# メール送信関数
def send_verification_email(email, token):
  try:
    # config.pyで設定したFRONTEND_BASE_URLを使用
    verification_link = f"{current_app.config.get('FRONTEND_BASE_URL')}/verify-email?token={token}"

    msg = Message('【ShareFood】アカウント認証のお願い', recipients=[email])
    msg.body = textwrap.dedent(f"""\
    この度はご登録いただきありがとうございます。
    アカウントを認証するには、以下のリンクをクリックしてください:
    {verification_link}
    このリンクは有効期限が設定されています。
    もしこのメールに心当たりがない場合は、無視してください。
    """)
    mail.send(msg)
    current_app.logger.info(f"認証メールを {email} に送信しました。")
  except Exception as e:
    current_app.logger.error(f"認証メールの送信に失敗しました: {e}", exc_info=True)
    # 本番環境では、メール送信失敗をユーザーに通知するか、再試行メカニズムを設定