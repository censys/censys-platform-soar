from pydantic.types import UUID4
from soar_sdk.asset import AssetField, BaseAsset
from soar_sdk.logging import getLogger

logger = getLogger()


class Asset(BaseAsset):
    base_url: str = AssetField(default="https://api.platform.censys.io")
    api_token: str = AssetField(
        sensitive=True,
        description="Personal access token for authentication",
        required=True,
    )
    organization_id: UUID4 | None = AssetField(
        default=None,
        description="Organization ID for the organization you would like to act as",
    )
