import os
from flask import Flask, jsonify
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

# プロジェクトのルートディレクトリ (ShareFood-backend) を取得
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def create_app(testing=False, config_class=Config):
    """アプリケーションファクトリ関数"""
    # フロントエンドのビルドファイルが格納されている静的フォルダを明示的に指定
    # これでFlaskはどこにあるindex.htmlを返せばいいか分かるようになります
    static_folder_path = os.path.join(project_root, 'static')
    app = Flask(__name__, static_folder=static_folder_path, static_url_path='')

    # --- ここで渡されたconfig_classから設定を読み込む ---
    app.config.from_object(config_class)

    # --- 拡張機能の初期化 ---
    # ここで拡張機能をFlaskアプリに結びつける
    db.init_app(app)
    # render_as_batch=True は SQLite での制約変更をサポートするために推奨されます
    migrate.init_app(app, db, render_as_batch=True)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    jwt.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        # --- ルーティングとモデルのインポート ---
        # ファクトリ内でインポートすることで循環参照を避けます。
        from .routes import (
            register_route, login_route, profile_route, 
            logout_route, item_route, view_route
        )
        from . import models

        # ブループリントの登録
        app.register_blueprint(register_route.bp)
        app.register_blueprint(login_route.bp)
        app.register_blueprint(profile_route.bp)
        app.register_blueprint(logout_route.bp)
        app.register_blueprint(item_route.bp)
        app.register_blueprint(view_route.bp)
    
        # JWTのエラーハンドリングを追加すると、より親切なエラーメッセージを返せます
        @jwt.unauthorized_loader
        def unauthorized_callback(reason):
            return jsonify({"message": "リクエストには認証トークンが必要です"}), 401

        @jwt.invalid_token_loader
        def invalid_token_callback(error):
            return jsonify({"message": "無効な認証トークンです"}), 422

    return app
