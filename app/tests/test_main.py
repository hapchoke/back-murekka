import json
import os
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

parent_dir = os.path.abspath(os.path.join(os.getcwd()))
sys.path.append(parent_dir)
from dotenv import load_dotenv

from app import main
from app.database import Base

load_dotenv()

S3_BUCKET = os.getenv('S3_BUCKET')


SQLALCHEMY_DATABASE_URL = "sqlite:///./app/tests/test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


main.app.dependency_overrides[main.get_db] = override_get_db

client = TestClient(main.app)


# ファイルサイズとファイル名渡す
def test_send_add_get():
    response = client.post("/image", json={"file_size": "50000", "file_name": "Foo"})
    assert response.status_code == 200
    data = response.json()
    password = json.loads(data[0])["password"]


    response = client.post("/add-file-name", json={"password": password, "file_name": "Yoo"})
    assert response.status_code == 200

 
    response = client.get("/get-image/{0}".format(password))
    assert response.status_code == 200


# 1GBが以上ならエラー
def test_send_big_image():
    response = client.post("/image", json={"file_size": "1073741824", "file_name": "Foo"})
    assert response.status_code == 400
    assert response.json() == {"detail": "your file_size bigger than 1GB"}


# ファイル追加　パスワード違う
def test_add_file_name_inexistent_password():
    response = client.post("/add-file-name", json={"password": "CR1U", "file_name": "Yoo"})
    assert response.status_code == 400
    assert response.json() == {"detail": "your password do not match"}


# イメージ取得　パスワード違う
def test_get_image_url_inexistent_password():
    response = client.get("/get-image/CR1U")
    assert response.status_code == 400
    assert response.json() == {"detail": "your password do not match"}


# ヘルスチェックを返すか
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
