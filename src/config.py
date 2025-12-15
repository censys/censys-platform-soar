from typing import Self
from pydantic import Field, model_validator
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
    organization_id: str = Field(
        default=None,
        description="Organization ID for the organization you would like to act as",
    )

    @model_validator(mode="after")
    def validate_organization_id(self) -> Self:
        """Checks that organization_id is a valid UUIDv4"""
        try:
            UUID4(self.organization_id, version=4)
        except ValueError as err:
            raise ValueError(
                "'organization_id' must be a valid organization UUIDv4 or unset"
            ) from err
        return self
