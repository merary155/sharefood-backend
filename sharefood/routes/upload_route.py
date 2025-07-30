import os
from flask import Blueprint, request, current_app, jsonify
from werkzeug.utils import secure_filename

bp = Blueprint('upload_route', __name__, url_prefix='/api/v1')

@bp.route('/upload', methods=['POST'])
def upload_file():
  if 'images' not in request.files:
    return jsonify({'message': '画像ファイルがありません'}),400
  
  files = request.files.getlist('images')
  saved_files = []
  
  for file in files:
    if file.filename == '':
      continue
    filename = secure_filename(file.filename)
    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)
    saved_files.append(filename) # アップロードされたファイルを、安全に変換したファイル名 (filename)をリスト'saved_files'に追加
    
  return jsonify({'message': 'アップロード完了', 'files': saved_files}), 200


