from flask import Blueprint, jsonify
# 今後の実装で必要になるもの
# from flask import request
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_jwt_extended import create_access_token
# from .models import User
# from . import db

# Blueprintを作成
# 'api'はBlueprintの名前、__name__は現在のモジュール名、url_prefixでURLの先頭に/api/v1を付けます
bp = Blueprint('api', __name__, url_prefix='/api/v1')

@bp.route('/status')
def status():
  response_data = {'status': 'ok', 'message': 'Backend is running!'}
  return jsonify(response_data)

# 今後、/register や /login はここに追記していく

