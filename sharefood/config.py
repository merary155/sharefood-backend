import os
from datetime import timedelta
import sharefood

# __file__は今いるファイル
# os.path.dirname() を1回使う → 1階層上のディレクトリ
# 絶対パスは指定した階層のディレクトリーを取得
# ここでは"C:/.../sharefood-backend"をproject_rootに代入
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

UPLOAD_FOLDER = os.path.join(project_root, 'sharefood', 'static', 'uploads')

class Config:
  # --- データベースファイルのパスを設定 ---
  # 環境変数 DATABASE_URL があればそれを使用、なければ 'sqlite:///app.db' を使用
  # 'app.db' はプロジェクトルートに作成されます
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                            'sqlite:///' + os.path.join(project_root, 'app.db')
  
  # SQLAlchemyの追跡機能は不要なのでオフ
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  
  # JWTのためにSECRET_KEYも設定
  # SECRET_KEYは環境変数から読み込むのがベストプラクティス
  SECRET_KEY = os.environ.get('SECRET_KEY') or '64b0bb69cfbb45b39b5c1dba'
  
  # JWT専用の秘密鍵も設定（JWTの署名用）
  # JWT_SECRET_KEYも環境変数から読み込むのがベストプラクティス
  JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-super-secret-key'
  
  # JWTのトークン期限設定
  JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
  JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7) # リフレッシュトークンの有効期限を7日に設定

  # JWTの検索場所をヘッダーのみに限定
  JWT_TOKEN_LOCATION = ['headers']

  # 画像アップロードの保存先
  UPLOAD_FOLDER = UPLOAD_FOLDER
  ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class DevelopmentConfig(Config):
  # 開発環境用の設定
  DEBUG = True
  # 開発用に別のDBファイルを使用する場合
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                            'sqlite:///' + os.path.join(project_root, 'dev_app.db')

class TestingConfig(Config):
  # テスト環境用の設定
  TESTING = True
  SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # テスト用にインメモリDBを使用
  JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5) # テスト中はJWTの有効期限を短くする
  SECRET_KEY = 'test-secret-key-for-testing' # テスト用の秘密鍵
  JWT_SECRET_KEY = 'test-jwt-secret-key-for-testing' # テスト用のJWT秘密鍵


class ProductionConfig(Config):
  # 本番環境用の設定
  DEBUG = False
  # 本番環境では環境変数からの読み込みを必須にするなど
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') # 本番では環境変数必須
  SECRET_KEY = os.environ.get('SECRET_KEY') # 本番では環境変数必須
  JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') # 本番では環境変数必須
  # ログ設定などもここに追加