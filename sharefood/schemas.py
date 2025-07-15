import re
from marshmallow import Schema, fields, validate, ValidationError, validates

class RegisterSchema(Schema):
  username = fields.Str(
    required = True,
    validate = validate.Length(min=1, max=30, error="ユーザー名は必須です。")
  )
  email = fields.Email(
    required = True,
    error_messages={"invalid": "有効なメールアドレスを入力してください。"}
  )
  password = fields.Str(
    required = True,
    validate = validate.Length(min=8, error="パスワードは8文字以上で入力してください。"),
    load_only = True
  )

  @validates("password")
  def validate_password_strength(self, value):
    if not re.search(r'[A-Z]', value):
        raise ValidationError("パスワードには少なくとも1つの大文字が必要です。")
    if not re.search(r'[a-z]', value):
        raise ValidationError("パスワードには少なくとも1つの小文字が必要です。")
    if not re.search(r'[0-9]', value):
        raise ValidationError("パスワードには少なくとも1つの数字が必要です。")
    
class LoginSchema(Schema):
  email = fields.Email(
    required = True,
    error_messages={
      "invalid": "有効なメールアドレスを入力してください。", 
      "required": "メールアドレスは必須です。"
    }
  )

  password = fields.Str(
    required = True,
    error_messages={"required":"パスワードは必須です。"},
    load_only = True
  )