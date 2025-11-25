from censys_platform import models

from soar_sdk.abstract import SOARClient
from soar_sdk.exceptions import ActionFailure
from soar_sdk.app import App
from soar_sdk.logging import getLogger

from actions import get_cert, get_host, get_web_property
from config import Asset
from utils import create_censys_sdk, has_org_config

logger = getLogger()

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
    with create_censys_sdk(asset) as sdk:
        try:
            if has_org_config(asset):
                sdk.account_management.get_organization_details(
                    organization_id=str(asset.organization_id),
                    include_member_counts=False,
                )
            else:
                sdk.global_data.get_host(host_id="127.0.0.1")
            return
        except models.SDKBaseError as err:
            logger.error(err)
            raise ActionFailure(
                f"Connectivity test failed with status code {err.status_code}"
            ) from err
        except Exception as err:
            logger.error(err)
            raise ActionFailure("Connectivity test failed with generic error") from err


app.register_action(
    get_cert,
    name="Lookup Certificate",
    verbose="Retrieve a certificate by SHA256 fingerprint from the Censys Platform API",
    action_type="investigate",
)
app.register_action(
    get_host,
    name="Lookup Host",
    verbose="Retrieve a host by IP address from the Censys Platform API",
    action_type="investigate",
)
app.register_action(
    get_web_property,
    name="Lookup Web Property",
    verbose="Retrieve a web property by domain_name:port from the Censys Platform API",
    action_type="investigate",
)

if __name__ == "__main__":
    app.cli()
