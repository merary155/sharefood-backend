import os
from datetime import timedelta

import sharefood

# __file__は今いるファイル
# os.path.dirname() を1回使う → 1階層上のディレクトリ
# 絶対パスは指定した階層のディレクトリーを取得
# ここでは"C:/.../sharefood-backend"をproject_rootに代入
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# basedirはファイルがあるディレクトリの絶対パスを取得
basedir = os.path.abspath(os.path.dirname(__file__))

# --- データベースファイルのパスを設定 ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
# SQLAlchemyの追跡機能は不要なのでオフ
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWTのためにSECRET_KEYも設定
# JWTは一度ログインすれば署名付きトークンを発行し、有効期限内なら再ログイン不要になる
# そのおかげでYoutube,chatGPT等のサイトでログイン状態が維持される
app.config['SECRET_KEY'] = '64b0bb69cfbb45b39b5c1dba'

# JWT専用の秘密鍵も設定（JWTの署名用）
app.config['JWT_SECRET_KEY'] = 'your-jwt-super-secret-key'
# JWTのトークン期限設定
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(weeks=2) 