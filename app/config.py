from pydantic import BaseSettings

class Settings(BaseSettings):
    S3_BUCKET : str
    AWS_ACCESS_KEY_ID : str
    AWS_SECRET_ACCESS_KEY : str
    class Config:
        env_file = ".env"

# from dotenv import load_dotenv
# load_dotenv()

# # 環境変数を参照
# import os
# AWS_ACCESS_KEY_ID=os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SECRET_ACCESS_KEY')
# S3_BUCKET=os.getenv('S3_BUCKET')