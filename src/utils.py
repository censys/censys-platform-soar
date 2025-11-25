import ipaddress

from censys_platform import SDK

from soar_sdk.logging import getLogger

from config import Asset

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
        organization_id=str(asset.organization_id),
        personal_access_token=asset.api_token,
        server_url=asset.base_url,
    )


def is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
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
