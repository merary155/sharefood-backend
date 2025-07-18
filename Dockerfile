# --- ベースイメージの指定 ---
# Python 3.10 の軽量なイメージをベースにします
FROM python:3.10-slim

# --- 作業ディレクトリの設定 ---
# コンテナ内の /app ディレクトリで作業します
WORKDIR /app

# --- 依存関係のインストール ---
# まず requirements.txt だけをコピーして、ライブラリをインストールします。
# こうすることで、アプリケーションのコードを変更しただけでは再インストールが走らず、ビルドが高速になります。
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- アプリケーションコードのコピー ---
# プロジェクトのファイルを作業ディレクトリにコピーします
COPY . .

# --- 非rootユーザーの作成と利用 ---
# セキュリティ向上のため、専用の非rootユーザーを作成してアプリケーションを実行します
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# アプリケーションを実行するユーザーを切り替えます
USER appuser

# --- ポートの公開 ---
# Flaskアプリケーションがリッスンするポートを公開します
EXPOSE 5000

# --- アプリケーションの実行コマンド ---
# コンテナが起動したときに、Gunicornを使ってアプリケーションを実行します
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]