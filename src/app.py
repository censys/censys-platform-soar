from soar_sdk.abstract import SOARClient
from soar_sdk.app import App
from soar_sdk.asset import AssetField, BaseAsset
from soar_sdk.logging import getLogger

logger = getLogger()


class Asset(BaseAsset):
    base_url: str = AssetField(default="https://api.platform.censys.io")
    api_token: str = AssetField(
        sensitive=True, description="Personal access token for authentication"
    )
    organization_id = AssetField(
        default=None,
        description="Organization ID for the organization you would like to act as",
    )


app = App(
    name="censys-platform-soar",
    app_type="investigative",
    logo="logo_censys.svg",
    logo_dark="logo_censys_dark.svg",
    product_vendor="Censys",
    product_name="Censys Platform API",
    publisher="Censys",
    appid="15d8b3a4-9910-4ac8-bd64-933168fc03ca",
    fips_compliant=False,
    asset_cls=Asset,
)


@app.test_connectivity()
def test_connectivity(soar: SOARClient, asset: Asset) -> None:
    raise NotImplementedError()


if __name__ == "__main__":
    app.cli()
