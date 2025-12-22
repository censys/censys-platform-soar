from censys_platform import models
from pydantic import Field
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, ActionResult
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger
from soar_sdk.params import Param, Params

from ..config import Asset
from ..utils import (
    create_censys_sdk,
    get_attr_path,
    is_valid_at_time,
    is_valid_web_property_hostname,
)
from .action_output import CensysActionOutput
from .utils import format_software, extract_cert_fields


logger = getLogger()


class GetWebPropertyActionParams(Params):
    hostname: str
    port: int = Field(gte=1, lte=65535)
    at_time: str = Param(
        default=None,
        required=False,
        description="The historical timestamp to retrieve web property data for. If unspecified, we will retrieve the latest data.",
    )


class GetWebPropertyActionOutput(CensysActionOutput):
    web: models.Webproperty


class GetWebPropertyActionSummary(ActionOutput):
    hostname: str
    port: int
    scan_time: str
    endpoints: list[str]
    endpoint_count: int


def lookup_web_property(
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
                at_time=str(params.at_time) if params.at_time else None,
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
        f"Web Property '{data.hostname}:{data.port}' has {len(data.endpoints):,} visible endpoint(s)"
    )

    return GetWebPropertyActionOutput(web=data)


def lookup_web_property_view_handler(
    all_outputs: list[GetWebPropertyActionOutput],
) -> dict:
    return {
        "results": [
            {
                "hostname": output.web.hostname,
                "port": output.web.port,
                "scan_time": get_attr_path(output, "web.scan_time", "N/A"),
                "software": render_software(output),
                "endpoints": render_endpoints(output),
                "cert": extract_cert_fields(get_attr_path(output, "web.cert", None)),
            }
            for output in all_outputs
        ],
        "total_count": len(all_outputs),
    }


def render_software(output: GetWebPropertyActionOutput) -> list[str]:
    software_set: set[str] = set()

    for software in get_attr_path(output, "web.software", None):
        formatted = format_software(
            getattr(software, "vendor", None),
            getattr(software, "product", None),
            getattr(software, "version", None),
        )
        if formatted:
            software_set.add(formatted)

    return sorted(list(software_set))


def render_endpoints(output: GetWebPropertyActionOutput) -> list[dict]:
    endpoints = get_attr_path(output, "web.endpoints", [])
    if not endpoints:
        return []

    return [
        {
            "path": getattr(ep, "path", None),
            "endpoint_type": getattr(ep, "endpoint_type", None),
        }
        for ep in endpoints
    ]
