from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from .config import Config

# --- 拡張機能のインスタンスを作成 ---
db = SQLAlchemy()    # SQLAlchemyを利用するためのオブジェクト
migrate = Migrate()  # マイグレーションを管理するオブジェクト
cors = CORS()        # frontendとbackendを繋げるためのCORS設定用オブジェクト
jwt = JWTManager()   # JWT（JSON Web Token）を扱うオブジェクト
bcrypt = Bcrypt()    # パスワードをハッシュ化するオブジェクト

def create_app(testing=False, config_class=Config):
    """アプリケーションファクトリ関数"""
    app = Flask(__name__)

    # --- ここで渡されたconfig_classから設定を読み込む ---
    app.config.from_object(config_class)

    # --- 拡張機能の初期化 ---
    # ここで拡張機能をFlaskアプリに結びつける
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    jwt.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        # --- ルーティングとモデルのインポート ---
        # ファクトリ内でインポートすることで循環参照を避けます。
        from .routes import register_route, login_route, profile_route, logout_route, item_route
        from . import models

        # ブループリントの登録
        app.register_blueprint(register_route.bp)
        app.register_blueprint(login_route.bp)
        app.register_blueprint(profile_route.bp)
        app.register_blueprint(logout_route.bp)
        app.register_blueprint(item_route.bp)
    
    return app
