import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# --- 拡張機能のインスタンスを作成 ---
db = SQLAlchemy()    # SQLAlchemyを利用するためのオブジェクト
migrate = Migrate()  # マイグレーションを管理するオブジェクト
cors = CORS()        # frontendとbackendを繋げるためのCORS設定用オブジェクト
jwt = JWTManager()   # JWT（JSON Web Token）を扱うオブジェクト
bcrypt = Bcrypt()    # パスワードをハッシュ化するオブジェクト
login_manager = LoginManager() # ログイン管理用のオブジェクト

def create_app():
    """アプリケーションファクトリ関数"""
    app = Flask(__name__)
    # basedirはファイルがあるディレクトリの絶対パスを取得している
    basedir = os.path.abspath(os.path.dirname(__file__))

    # --- データベースファイルのパスを設定 ---
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    # SQLAlchemyの追跡機能は不要なのでオフに
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # JWTのためにSECRET_KEYも設定
    # JWTは一度ログインすれば署名付きトークンを発行し、有効期限内なら再ログイン不要になる
    # そのおかげでYoutube,chatGPT等のサイトでログイン状態が維持される
    app.config['SECRET_KEY'] = '64b0bb69cfbb45b39b5c1dba'

    # JWT専用の秘密鍵も設定（JWTの署名用）
    app.config['JWT_SECRET_KEY'] = 'your-jwt-super-secret-key'

    # --- 拡張機能の初期化 ---
    # ここで拡張機能をFlaskアプリに結びつける
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    jwt.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        # --- ルーティングとモデルのインポート ---
        # ファクトリ内でインポートすることで循環参照を避けます。
        from .routes import register_route, login_route
        from . import models

        # ブループリントの登録
        app.register_blueprint(register_route.bp)
        app.register_blueprint(login_route.bp)
    
    return app
