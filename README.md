# 無劣化転送
画像を気軽にアップロード、ダウンロードできます。
https://harukifreedomein.tk/
# 使用技術
- FastAPI/Python
- alembic
- React.js
- AWS/S3/FARGATE/RDS/ALB/Route53/CloudFront・・・・
- Docker
- html/css/javascript
# インフラ構成図
![This is an image](./media/infra-stracture.png)
- フロント(サイトの表示)はS3の静的ウェブサイトホスティングをCloudFront+Route53でカスタムドメイン付きのhttps通信
- サーバーサイドはpublic subnetにfargate、private subnetにPostgreSQL、fargateの前にACMの証明書をいれたALBを配置しhttps通信
- ストレージはS3
# 機能一覧
- 画像のアップロード、ダウンロード、拡大表示
# フロントのコード
https://github.com/hapchoke/front-murekka