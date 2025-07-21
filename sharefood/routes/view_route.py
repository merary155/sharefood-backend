import os
from flask import Blueprint, send_from_directory, current_app, abort

bp = Blueprint('view_route', __name__)

# このルートは、APIルート以外のすべてのGETリクエストを捕捉します。
# これにより、React RouterのようなクライアントサイドルーターがURLの制御を行えるようになります。
@bp.route('/', defaults={'path': ''})
@bp.route('/<path:path>')
def serve_react_app(path):
  # もしリクエストがAPIへのものであれば、この案内係は「私の仕事ではない」として処理を中断します。
  # これにより、Flaskは他の適切なAPIルート（コックさん）を探しに行きます。
  if path.startswith('api/'):
    abort(404)

  # __init__.pyで設定した静的フォルダの場所を取得します。
  static_folder = current_app.static_folder

  # リクエストされたパスが実在するファイル（例: favicon.ico）なら、それを返します。
  if path != "" and os.path.exists(os.path.join(static_folder, path)):
    return send_from_directory(static_folder, path)
  else:
    # それ以外（/login, /registerなど）の場合は、Reactアプリ本体である index.html を返します。
    # これでホール係（React）に仕事が引き渡されます。
    return send_from_directory(static_folder, 'index.html')