#!/usr/bin/env python3
import os, boto3
from pathlib import Path
from botocore.config import Config
def main():
    bucket = os.getenv("S3_INPUT_BUCKET","").strip()
    prefix = os.getenv("S3_INPUT_PREFIX","").strip()
    outdir = Path(os.getenv("LOCAL_DATA_ROOT",".")).expanduser()
    outdir.mkdir(parents=True, exist_ok=True)
    if not bucket or not prefix:
        print("Nothing to fetch: missing S3_INPUT_BUCKET or S3_INPUT_PREFIX"); return
    print(f"Downloading s3://{bucket}/{prefix} → {outdir}")
    s3 = boto3.client("s3", config=Config(max_pool_connections=32))
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith("/"):
                continue
            dst = outdir / Path(key).name
            if dst.exists():
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            s3.download_file(bucket, key, str(dst))
            print("✓", key, "→", dst)
if __name__ == "__main__":
    main()
