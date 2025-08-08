from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from ..models import User
from .. import db

bp = Blueprint('verify_email_route', __name__, url_prefix='/api/v1')

# メール認証API
@bp.route('/verify-email', methods=['GET'])
def verify_email():
  token = request.args.get('token') # URLクエリパラメータからトークンを取得

  if not token:
    return jsonify({'message': '認証トークンが指定されていません。'}), 400

  user = User.query.filter_by(verification_token=token).first()

  if not user:
    current_app.logger.warning(f"無効な認証トークンが使用されました: {token}") # ログチェック用
    return jsonify({'message': '無効な認証トークンです。'}), 404

  # トークンの有効期限チェック
  # SQLiteはタイムゾーンをネイティブにサポートしないため、テスト実行時にDBから取得した
  # 日時がnaive(タイムゾーン情報なし)になる。これをaware(情報あり)に変換してから比較する。
  expires_at = user.token_expires_at
  if expires_at and expires_at.tzinfo is None:
    expires_at = expires_at.replace(tzinfo=timezone.utc)

  if not expires_at or expires_at < datetime.now(timezone.utc):
    current_app.logger.info(f"期限切れトークン使用: {token}") # ログチェック用
    return jsonify({'message': '認証トークンの有効期限が切れています。'}), 400

  # ユーザーを認証済みとしてマーク
  user.is_verified = True
  user.verification_token = None # トークンを使用済みとしてクリア
  user.token_expires_at = None   # 有効期限もクリア

  try:
    db.session.commit()  # DBコミット処理を try-exceptで囲み例外対応
  except Exception as e:
    current_app.logger.error(f"DBコミット失敗: {e}", exc_info=True)
    return jsonify({'message': 'サーバーエラーが発生しました。'}), 500

  return jsonify({'message': 'メールアドレスが正常に認証されました。'}), 200