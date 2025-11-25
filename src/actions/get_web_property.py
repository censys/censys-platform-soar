from censys_platform import models
from pydantic import Field
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, ActionResult
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger
from soar_sdk.params import Param, Params

from config import Asset
from utils import create_censys_sdk, is_valid_at_time, is_valid_web_property_hostname

logger = getLogger()


class GetWebPropertyActionParams(Params):
    hostname: str
    port: int = Field(gte=1, lte=65535)
    at_time: str | None = Param(
        default=None,
        required=False,
        description="The historical timestamp to retrieve web property data for. If unspecified, we will retrieve the latest data.",
    )


class GetWebPropertyActionOutput(ActionOutput):
    web: models.Webproperty


class GetWebPropertyActionSummary(ActionOutput):
    hostname: str
    port: int
    scan_time: str
    endpoints: list[str]
    endpoint_count: int


def get_web_property(
    params: GetWebPropertyActionParams,
    asset: Asset,
    soar: SOARClient[GetWebPropertyActionSummary],
) -> GetWebPropertyActionOutput:
    """
    Retrieves a web property by domain_name:port
    """
    if not is_valid_web_property_hostname(params.hostname):
        return ActionResult(
            False,
            "Please provide a valid domain name or IP address value in the 'hostname' action parameter",
            dict(params),
        )

    if params.at_time is not None and not is_valid_at_time(params.at_time):
        return ActionResult(
            False,
            "Please provide a valid ISO 8601 timestamp in the 'at_time' action parameter, or leave it unset",
            dict(params),
        )

    web_property_id = f"{params.hostname}:{params.port}"
    logger.info(
        f"Loading web property with ID {web_property_id} (at_time: {params.at_time if params.at_time is not None else 'unspecified'})"
    )
    data: models.Webproperty | None = None

    with create_censys_sdk(asset) as sdk:
        try:
            res = sdk.global_data.get_web_property(
                webproperty_id=web_property_id,
                at_time=str(params.at_time) if params.at_time is not None else None,
            )
            data = res.result.result.resource
            logger.debug("Successfully retrieved web property")
        except models.SDKBaseError as err:
            logger.error(err)
            raise ActionFailure(
                f"Failed to retrieve web property with status code: {err.status_code}"
            ) from err
        except Exception as err:
            logger.error(err)
            raise ActionFailure(
                "Failed to retrieve web property with generic error"
            ) from err

    soar.set_summary(
        GetWebPropertyActionSummary(
            hostname=data.hostname,
            port=data.port,
            scan_time=data.scan_time,
            endpoints=[e.path for e in data.endpoints],
            endpoint_count=len(data.endpoints),
        )
    )
    soar.set_message(
        f"Web Property '{data.hostname}:{data.port}' has {len(data.endpoints)} visible endpoint(s)"
    )

    return GetWebPropertyActionOutput(web=data)
