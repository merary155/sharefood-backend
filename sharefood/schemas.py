import re
from typing import Required
from marshmallow import Schema, fields, validate, ValidationError, validates

# UserとItemのインスタンスのみをここで生成してるのはほかの場所で使いまわすから
# RegisterとLoginは使う場所が限定されてるのでそのスコープ内でインスタンスを生成する

# --- Registerのスキーマ ---   
class RegisterSchema(Schema):
  username = fields.Str(
    required = True,
    validate = validate.Length(min=1, max=30, error="ユーザー名は必須です。")
  )
  email_address = fields.Email(
    required = True,
    error_messages={"invalid": "有効なメールアドレスを入力してください。"}
  )
  password = fields.Str(
    required = True,
    validate = validate.Length(min=8, error="パスワードは8文字以上で入力してください。"),
    load_only = True
  )

  @validates("password")
  # 第2引数'data_key'は追加でチェックしたいものがある場合、デフォルトはNone（無し）
  def validate_password_strength(self, value, data_key=None):
    if not re.search(r'[A-Z]', value):
      raise ValidationError("パスワードには少なくとも1つの大文字が必要です。")
    if not re.search(r'[a-z]', value):
      raise ValidationError("パスワードには少なくとも1つの小文字が必要です。")
    if not re.search(r'[0-9]', value):
      raise ValidationError("パスワードには少なくとも1つの数字が必要です。")

# --- Loginのスキーマ ---    
class LoginSchema(Schema):
  email_address = fields.Email(     # 値がメールアドレス形式であることをチェックするフィールド型。@example.com がないと弾かれる
    required = True,
    error_messages={
      "invalid": "有効なメールアドレスを入力してください。",  # 入力ないときはこのメッセージ
      "required": "メールアドレスは必須です。"              # 入力あって形式が違ったときはこのメッセージ
    }
  )

  password = fields.Str(
    required = True,
    error_messages={"required":"パスワードは必須です。"},
    load_only = True
  )

# --- Userのスキーマ ---
class UserSchema(Schema):
  # dump_only=True を設定することで、このフィールドは読み取り専用になる
  # APIのレスポンスには含まれますが、リクエストボディで送られてきても無視される
  # IDはサーバー側で自動採番されるため、クライアントから変更されるべきではないため
  id = fields.Int(dump_only=True)
  username = fields.Str()
  email_address = fields.Email()

user_schema = UserSchema()

# --- Itemのスキーマ ---
class ItemSchema(Schema):
  # 読み取り専用フィールド（APIレスポンスにのみ含める）
  id = fields.Int(dump_only=True)
  created_at = fields.DateTime(dump_only=True, format='%Y-%m-%dT%H:%M:%S')

  # 書き込み・読み取り可能フィールド（バリデーションルールも設定）
  name = fields.Str(required=True, validate=validate.Length(min=1, max=50, error="食品名は1文字以上50文字以下で入力してください。"))
  description = fields.Str(validate=validate.Length(max=255, error="説明文は255文字以下で入力してください。"))
  quantity = fields.Int(required=True, validate=validate.Range(min=1, error="数量は1以上で入力してください。"))
  image_path = fields.Str(dump_only=True) # 画像パスは読み取り専用
  unit = fields.Str(load_default='個', dump_default='個') # 単位
  expiration_date = fields.Date() # YYYY-MM-DD形式
  location = fields.Str(validate=validate.Length(max=120, error="場所は120文字以下で入力してください。"))
  is_available = fields.Bool(load_default=True, dump_default=True)

  # user_id は直接公開せず、代わりにネストしたユーザー情報を含める
  # これにより、APIのレスポンスに「誰が出品したか」という情報を含められる
  user = fields.Nested(UserSchema, only=['id', 'username'], dump_only=True)

# 単一のItemオブジェクトを扱うためのスキーマインスタンス
item_schema = ItemSchema()
# 複数のItemオブジェクト（リスト）を扱うためのスキーマインスタンス
items_schema = ItemSchema(many=True)