import datetime
import hashlib
import json
import secrets
import string
from functools import lru_cache

import boto3
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import config, database, models

app = FastAPI()
# s3のポリシーで絞る
# origins = [
#     "http://localhost:8080"
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 環境変数取得
@lru_cache()
def get_settings():
    return config.Settings()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_random_password_string(length):
    # アルファベットの大小と0~9とurlに使える記号
    pass_chars = string.ascii_letters + string.digits + '-_'
    password = ''.join(secrets.choice(pass_chars) for x in range(length))
    return password


def get_random_string(length):
    chars = string.ascii_letters
    word = ''.join(secrets.choice(chars) for x in range(length))
    return word


def get_hashed_password_string(str):
    return hashlib.sha224(str.encode()).hexdigest()


def create_s3_sign(entry_point, file_name, s3, bucket):
    presigned_post = s3.generate_presigned_post(
        Bucket=bucket,
        Key=entry_point+file_name,
        Fields={"success_action_status": "201"},
        Conditions=[
            {"success_action_status": "201"}
        ],
        ExpiresIn=3600
    )
    return presigned_post

# リクエスト(file_size,)を受けたら、file_size確認し、s3用file_path,取得用url(password入り)を返す　　
# 現時刻,hashed-password,s3用path(重要な部分のみ)file_nmeをdb保存
# 24時間以上経ったファイルを削除する。


@app.post("/image")
def storage_image(user_file: models.UserFile, db: Session = Depends(get_db), settings: config.Settings = Depends(get_settings)):
    KB = 1024
    MB = 1024 * KB
    GB = 1024 * MB

    if user_file.file_size >= 1*GB:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="your file_size bigger than 1GB")

    # ファイルは分類する　modelでアップロード位置をs3のエンドポイント下に日付ディレクトリ、ユーザ毎文字列ディレクトリ、その下にメディアを置く
    today_dir = "fast" + str(datetime.date.today())
    user_dir = get_random_string(7)
    entry_point = "{0}/{1}/".format(today_dir, user_dir)
    # 数列作成
    sequence = get_random_password_string(15)
    # 数列が漏れた時純正のルートからアクセスされてしまうのを防ぐため　ハッシュ化しておく
    hashed_password = get_hashed_password_string(sequence)

    # dbにrequest情報　保存　
    models.create_trial(db, file_path=entry_point, hashed_password=hashed_password, file_name=user_file.file_name)

    S3_BUCKET = settings.S3_BUCKET
    s3 = boto3.client('s3')
    # 署名を送る　
    presigned_post = create_s3_sign(entry_point, user_file.file_name, s3, S3_BUCKET)
    try:
        yield json.dumps({
            'password': sequence,
            'fields': presigned_post
            })
    finally:
        # その後に過去のデータを消している
        models.clean_up(db, bucket=settings.S3_BUCKET)
    

@app.post("/add-file-name")
def add_file_name(request: models.AddFileName, db: Session = Depends(get_db), settings: config.Settings = Depends(get_settings)):
    hashed_password = get_hashed_password_string(request.password)
    add_data = models.add_file_name(db, hashed_password=hashed_password, file_name=request.file_name)
    if add_data:
        S3_BUCKET = settings.S3_BUCKET
        s3 = boto3.client('s3')
        presigned_post = create_s3_sign(add_data['trial'].file_path, add_data['file_name'].file_name, s3, S3_BUCKET)
        return json.dumps({
            'fields': presigned_post
        })
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="your password do not match")


@app.get("/get-image/{password}")
def get_image_file(password: str, db: Session = Depends(get_db), settings: config.Settings = Depends(get_settings)):
    print("yo")
    hashed_password = get_hashed_password_string(password)
    print("ka")
    db_data = models.verify_password(db, hashed_password=hashed_password)
    print(db_data)
    if db_data:
        file_name = models.get_file_name_list(db, trial_id=db_data.id)
        # ファイルネームのリスト　と　entry_pointを合成して渡す
        S3_BUCKET = settings.S3_BUCKET
        url_common_part = "https://{0}.s3.amazonaws.com/".format(S3_BUCKET)
        # path作成
        url = ""
        for file_name in file_name:
            url = "{0}{1}{2}{3}:::".format(url, url_common_part, db_data.file_path, file_name.file_name)
        return json.dumps({
            "url": url
        })
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="your password do not match")


@app.get("/health", status_code=200)
async def health_check():
    return "200"

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)