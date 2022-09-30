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
![This is an image](./media/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202022-09-30%20%E5%8D%88%E5%BE%8C3.22.23.png)
- フロント(サイトの表示)はS3の静的ウェブサイトホスティングをCloudFront+Route53でカスタムドメイン付きのhttps通信
- サーバーサイドはpublic subnetにfargate、private subnetにPostgreSQL、fargateの前にACMの証明書をいれたALBを配置しhttps通信
- ストレージはS3
# 機能一覧
- 画像のアップロード、ダウンロード、拡大表示
# フロントのコード
https://github.com/hapchoke/front-murekka