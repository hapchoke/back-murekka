import datetime
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey,Integer,DateTime,String
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship
import boto3
from app import database
# alembic用
# import database


class Trial(database.Base):
    __tablename__="image_trial"
    id = Column(Integer,primary_key = True, autoincrement=True,unique=True)
    file_path = Column(String,unique = True)
    hashed_password = Column(String,unique=True)
    time = Column(DateTime(timezone=True), default=datetime.datetime.now)
    file_names = relationship("FileName")

# 外部キー　として作成
class FileName(database.Base):
    __tablename__="file_name"
    id = Column(Integer,primary_key = True, autoincrement=True,unique=True)
    file_name = Column(String)
    trial_id = Column(Integer,ForeignKey("image_trial.id"))


# crud
def create_trial(db:Session,file_path:str,hashed_password:str,file_name:str):
    db_item = Trial(file_path=file_path,hashed_password=hashed_password)
    db.add(db_item)
    db.commit()
    db_file_name = FileName(file_name=file_name,trial_id=db_item.id)
    db.add(db_file_name)
    db.commit()
    db.refresh(db_item)
    return db_item
def verify_password(db:Session,hashed_password:str):
    return db.query(Trial).filter(Trial.hashed_password==hashed_password).first()
def add_file_name(db:Session,hashed_password:str,file_name:str):
    trial = db.query(Trial).filter(Trial.hashed_password==hashed_password).first()
    if trial:
        db_file_name = FileName(file_name=file_name,trial_id=trial.id)
        db.add(db_file_name)
        db.commit()
        db.refresh(db_file_name)
        return {'file_name':db_file_name,'trial':trial}
    else:
        print("ファイルの追加に失敗しました。")
        return
def get_file_name_list(db:Session,trial_id:int):
    return db.query(FileName).filter(FileName.trial_id==trial_id)

def clean_up(db:Session,bucket:str):
#  ここで保存期間を設定
    target_time = datetime.datetime.now() - datetime.timedelta(days=1)
    target = db.query(Trial).filter(Trial.time < target_time)

    for target in target:
        attached_file_name = db.query(FileName).filter(FileName.trial_id==target.id)
        for file_name in attached_file_name:
            s3 = boto3.client('s3')
            url = "{0}{1}".format(target.file_path,file_name.file_name)
            s3.delete_object(Bucket=bucket, Key=url)
            db.delete(file_name)
            db.commit()
        db.delete(target)
        db.commit()


# schemas
class UserFile(BaseModel):
    file_size:int
    file_name:str

class AddFileName(BaseModel):
    file_name:str
    password:str