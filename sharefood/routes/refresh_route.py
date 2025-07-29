from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

bp = Blueprint('refresh_route', __name__, url_prefix='/api/v1')

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
  """
  リフレッシュトークンを使って新しいアクセストークンを生成するエンドポイント
  """
  current_user_id = get_jwt_identity()
  new_access_token = create_access_token()
  return jsonify({'access_token': new_access_token}), 200

