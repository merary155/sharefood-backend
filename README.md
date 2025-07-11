こちらは「ShareFood」サービスのバックエンドのリポジトリになります。フロントエンドのリポジトリは[こちら](https://github.com/merary155/sharefood-frontend)です。

# ShareFood / フードシェアサービス

## 📌 概要
**ShareFood** は、家庭や店舗で余ってしまった食品を地域の人々と「シェア」することで、  
食品廃棄を減らし、持続可能な社会を目指すフードシェアリングプラットフォームです。

## 仕様技術一覧
**フロントエンド** React.js 18.2.0/
- フォーマッター: Prettier
- テストフレームワーク: Jest / React Testing Library
- CSSフレームワーク: Tailwind CSS

**バックエンド:** Python 3.10.6 / Flask 3.1.1  
<details>
  <summary> 使用ライブラリ</summary>

- Flask 3.1.1（Webフレームワーク）  
- Flask-SQLAlchemy（ORM：DB操作）  
- Flask-WTF（フォームバリデーション）  
- WTForms（フォーム定義）  
- SQLAlchemy（DBライブラリ） 
</details>

- コード解析 / フォーマッター: flake8, black  
- テストフレームワーク: pytest, unittest  
- DB: SQLite  

**インフラ:** AWS(Route53 / Certificate Manager / ALB / VPC / ECR / ECS Fargate / RDS MySQL / S3) / Nginx / Vercel

**CI / CD:** GitHub Actions

**環境構築:** Docker / Docker Compose

**認証:** Firebase Authentication

## 主要対応一覧

### ユーザー向け

#### 機能
