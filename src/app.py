from censys_platform import models

from soar_sdk.abstract import SOARClient
from soar_sdk.exceptions import ActionFailure
from soar_sdk.app import App
from soar_sdk.logging import getLogger

from .actions.registration import register_all_actions
from .config import Asset
from .utils import create_censys_sdk, has_org_config

logger = getLogger()

app = App(
    name="Censys",
    app_type="investigative",
    logo="logo_censys.png",
    logo_dark="logo_censys.png",
    product_vendor="Censys",
    product_name="Censys Platform",
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
                    organization_id=asset.organization_id,
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


register_all_actions(app)

if __name__ == "__main__":
    app.cli()
