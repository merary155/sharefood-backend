from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

# --- 拡張機能のインスタンスを作成 ---
db = SQLAlchemy()    # SQLAlchemyを利用するためのオブジェクト
migrate = Migrate()  # マイグレーションを管理するオブジェクト
cors = CORS()        # frontendとbackendを繋げるためのCORS設定用オブジェクト
jwt = JWTManager()   # JWT（JSON Web Token）を扱うオブジェクト
bcrypt = None        # パスワードをハッシュ化するオブジェクト（後で初期化）
login_manager = None # ログイン管理用のオブジェクト（後で初期化）

# プロジェクトのルートディレクトリを取得
# basedir = os.path.abspath(os.path.dirname(__file__)) 
# これはファイルがあるディレクトリの絶対パスを取得している
basedir = os.path.abspath(os.path.dirname(__file__))

# Flaskアプリの作成
app = Flask(__name__)

# CORS(app)  # frontendとbackendを繋げるためのもの
# FlaskアプリにCORS設定を適用。クロスオリジン通信を許可する。
cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

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

# --- ログイン管理用の初期化 ---
login_manager = LoginManager(app)

# --- パスワードハッシュ化用の初期化 ---
bcrypt = Bcrypt(app)

# --- 拡張機能の初期化 ---
db.init_app(app)       # SQLAlchemyをFlaskアプリに結びつける
migrate.init_app(app, db) # マイグレーション機能をFlaskアプリとDBに結びつける
jwt.init_app(app)      # JWTの機能をFlaskアプリに結びつける

# ここからルーティングやモデルのインポートなどをするのが普通
# 例:
# from . import models
# from . import routes
# app.register_blueprint(routes.bp)