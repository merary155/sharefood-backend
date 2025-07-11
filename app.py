from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/v1/status')
def status():
  # Pythonの辞書を定義
  response_data = {'status': 'ok', 'message': 'Backend is running!'}
  # jsonifyを使ってJSON形式でレスポンスを返す
  return jsonify(response_data)

if __name__ == '__main__':
  app.run(debug=True)