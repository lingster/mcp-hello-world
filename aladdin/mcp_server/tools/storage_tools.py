"""MCP tools for Aladdin S3 storage operations."""

from __future__ import annotations

import json

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.config import server_config

_s3_client: _S3ClientWrapper | None = None


class _S3ClientWrapper:
    """Lightweight S3 client wrapping boto3."""

    def __init__(self) -> None:
        import boto3
        from botocore.config import Config

        cfg = server_config.s3
        if not all([cfg.endpoint_url, cfg.access_key_id, cfg.secret_access_key]):
            raise RuntimeError(
                "S3 not configured. Set ASDK_STORAGE__S3__ENDPOINT_URL, "
                "ASDK_STORAGE__S3__ACCESS_KEY_ID, and ASDK_STORAGE__S3__SECRET_ACCESS_KEY."
            )

        s3_config = Config(connect_timeout=30, retries={"max_attempts": 1})
        self.client = boto3.client(
            "s3",
            aws_access_key_id=cfg.access_key_id,
            aws_secret_access_key=cfg.secret_access_key,
            endpoint_url=cfg.endpoint_url,
            verify=True,
            config=s3_config,
        )
        self.default_bucket = cfg.bucket_name


def _get_s3() -> _S3ClientWrapper:
    global _s3_client
    if _s3_client is None:
        _s3_client = _S3ClientWrapper()
    return _s3_client


def register_storage_tools(mcp: FastMCP) -> None:
    """Register S3 storage tools with the MCP server."""

    @mcp.tool()
    def list_s3_objects(bucket_name: str | None = None) -> str:
        """List objects in an S3 bucket.

        Args:
            bucket_name: Bucket name (uses default if not provided)

        Returns:
            JSON list of objects with Key, Size, LastModified.
        """
        try:
            s3 = _get_s3()
            bucket = bucket_name or s3.default_bucket
            if not bucket:
                return json.dumps({"error": "No bucket name provided and no default configured"})

            response = s3.client.list_objects_v2(Bucket=bucket)
            objects = response.get("Contents", [])
            return json.dumps({
                "bucket": bucket,
                "count": len(objects),
                "objects": [
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": str(obj["LastModified"]),
                    }
                    for obj in objects
                ],
            }, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to list S3 objects: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def download_s3_object(key: str, bucket_name: str | None = None) -> str:
        """Download an S3 object and return its text content.

        Best for text files (JSON, CSV, etc.). For binary files, use
        download_s3_object_to_file instead.

        Args:
            key: S3 object key to download
            bucket_name: Bucket name (uses default if not provided)
        """
        try:
            s3 = _get_s3()
            bucket = bucket_name or s3.default_bucket
            if not bucket:
                return json.dumps({"error": "No bucket name provided and no default configured"})

            response = s3.client.get_object(Bucket=bucket, Key=key)
            body = response["Body"].read()

            # Try to decode as text
            try:
                content = body.decode("utf-8")
                # Try to parse as JSON for pretty printing
                try:
                    parsed = json.loads(content)
                    return json.dumps({
                        "key": key,
                        "bucket": bucket,
                        "content_type": "json",
                        "data": parsed,
                    }, indent=2, default=str)
                except json.JSONDecodeError:
                    return json.dumps({
                        "key": key,
                        "bucket": bucket,
                        "content_type": "text",
                        "data": content,
                    }, indent=2)
            except UnicodeDecodeError:
                return json.dumps({
                    "key": key,
                    "bucket": bucket,
                    "content_type": "binary",
                    "size_bytes": len(body),
                    "error": "Binary content cannot be displayed. Use download_s3_object_to_file.",
                })
        except Exception as e:
            logger.error(f"Failed to download S3 object {key}: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def upload_s3_object(key: str, content: str, bucket_name: str | None = None) -> str:
        """Upload text content as an S3 object.

        Args:
            key: S3 object key (path) to upload to
            content: Text content to upload
            bucket_name: Bucket name (uses default if not provided)
        """
        try:
            s3 = _get_s3()
            bucket = bucket_name or s3.default_bucket
            if not bucket:
                return json.dumps({"error": "No bucket name provided and no default configured"})

            s3.client.put_object(
                Bucket=bucket,
                Key=key,
                Body=content.encode("utf-8"),
            )
            return json.dumps({
                "status": "uploaded",
                "key": key,
                "bucket": bucket,
                "size_bytes": len(content.encode("utf-8")),
            }, indent=2)
        except Exception as e:
            logger.error(f"Failed to upload S3 object {key}: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def delete_s3_object(key: str, bucket_name: str | None = None) -> str:
        """Delete an object from S3.

        Args:
            key: S3 object key to delete
            bucket_name: Bucket name (uses default if not provided)
        """
        try:
            s3 = _get_s3()
            bucket = bucket_name or s3.default_bucket
            if not bucket:
                return json.dumps({"error": "No bucket name provided and no default configured"})

            s3.client.delete_object(Bucket=bucket, Key=key)
            return json.dumps({
                "status": "deleted",
                "key": key,
                "bucket": bucket,
            }, indent=2)
        except Exception as e:
            logger.error(f"Failed to delete S3 object {key}: {e}")
            return json.dumps({"error": str(e)})
