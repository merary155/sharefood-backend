from flask import Flask,render_template
from jinja2 import ChoiceLoader, FileSystemLoader

app = Flask(__name__)

# 複数のテンプレートフォルダを指定
app.jinja_loader = ChoiceLoader([
    FileSystemLoader('templates'),                     # 現プロジェクト内
    FileSystemLoader('../別リポジトリ/templates')       # 別リポジトリのtemplatesフォルダ（相対パス例）
])