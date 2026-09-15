import streamlit as st
import boto3
from botocore.config import Config

def upload_to_r2(file_bytes, file_name, content_type="application/zip"):
    try:
        if "r2" in st.secrets:
            r2_config = st.secrets["r2"]
            s3_client = boto3.client(
                "s3",
                endpoint_url=r2_config["endpoint_url"],
                aws_access_key_id=r2_config["aws_access_key_id"],
                aws_secret_access_key=r2_config["aws_secret_access_key"],
                config=Config(signature_version="s3v4"),
                region_name="auto"
            )
            s3_client.put_object(Bucket=r2_config["bucket_name"], Key=file_name, Body=file_bytes, ContentType=content_type)
            return s3_client.generate_presigned_url('get_object', Params={'Bucket': r2_config["bucket_name"], 'Key': file_name}, ExpiresIn=3600)
    except Exception as e:
        st.error(f"R2 Error: {e}")
    return None