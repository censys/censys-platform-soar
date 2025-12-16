from datetime import datetime
from ipaddress import ip_address
from typing import TypeVar

from censys_platform import SDK

from soar_sdk.logging import getLogger

from .config import Asset

logger = getLogger()


def has_org_config(asset: Asset) -> bool:
    return asset.organization_id is not None and str(asset.organization_id) != ""


def create_censys_sdk(asset: Asset) -> SDK:
    """
    Creates a pre-configured Censys SDK instance.
    """
    logger.debug(
        f"Creating Censys SDK with{' no' if not has_org_config(asset) else ''} org ID"
    )

    return SDK(
        organization_id=asset.organization_id,
        personal_access_token=asset.api_token,
        server_url=asset.base_url,
    )


def is_valid_ip(value: str) -> bool:
    try:
        ip_address(value)
    except ValueError:
        return False
    return True


def is_valid_web_property_hostname(value: str) -> bool:
    """
    Very naive validation of a bare domain name. Either accepts a valid IP address, or a
    dot-separated set of non-empty parts.
    """
    if is_valid_ip(value):
        return True

    parts = value.split(".")

    return len(parts) > 1 and all(len(p) > 0 for p in parts)


def is_valid_at_time(value: str) -> bool:
    """
    Validates that the given input is a valid ISO 8601 timestamp.
    """
    try:
        datetime.fromisoformat(value)
        return True
    except ValueError:
        return False


T = TypeVar("T")


def get_attr_path(obj: object, path: str, default: T = None) -> T:
    parts = path.split(".")
    curr = obj

    for attr in parts:
        if not hasattr(curr, attr):
            break

        curr = getattr(curr, attr, default)

    return curr
