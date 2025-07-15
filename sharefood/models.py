from . import db, bcrypt # __init__.pyで定義したインスタンスをインポート
from marshmallow import Schema, fields

# nullable そのcolumnに(null)を許すかどうか(許す→True)
# unique そのcolumnが他の行との重複を禁止にするかどうか→重複禁止(True)
# primary_keyは管理番号
# db.Column(...) がある → データベースのカラムとして認識される
# db.Modelを継承することによって下のデータがテーブルとして認識される
# Userが親（relationshipで所有を表現）、Itemが子（ForeignKeyで参照を表現）になる関係性
# ForeignKeyの指定は「'クラス名（小文字）.id'」の形式にする（SQLAlchemyの規約）

class User(db.Model):
  id = db.Column(db.Integer(), primary_key=True)
  username = db.Column(db.String(30), nullable=False)
  email_address = db.Column(db.String(120), unique=True, nullable=False)
  password_hash = db.Column(db.String(60), nullable=False)

  # ()が不要になり、関数を変数のように読み取れる
  # ただしここでは読み取りは禁止し、アクセスすると例外を出す
  @property
  def password(self):
    raise AttributeError('password is not a readable attribute')
  
  @password.setter
  # こっちはアカウント作成時にパスワードをハッシュ化する関数
  def password(self, plain_text_password):
    # Userの中のpassword_hashに代入するからself.password_hashにする    
    # この段階でUser.password_hash関数が呼び出されてハッシュ化する
    self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

  # こっちはログイン時にパスワードをハッシュ化する関数、上のハッシュ化パスワードと照合する
  def check_password(self, attempted_password):
    return bcrypt.check_password_hash(self.password_hash, attempted_password)
  
  def __repr__(self):
    return f'<User {self.username}>'