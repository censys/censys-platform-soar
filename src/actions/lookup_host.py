from censys_platform import models
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, ActionResult
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger
from soar_sdk.params import Param, Params

from ..config import Asset
from ..utils import create_censys_sdk, is_valid_at_time, is_valid_ip
from .action_output import CensysActionOutput

logger = getLogger()


class GetHostActionParams(Params):
    ip: str = Param(description="IPv4/IPv6 address for the host to lookup")
    at_time: str = Param(
        default=None,
        required=False,
        description="The historical timestamp to retrieve host data for. If unspecified, we will retrieve the latest data.",
    )


class GetHostActionOutput(CensysActionOutput):
    host: models.Host
    scan_time: str


class GetHostActionSummary(ActionOutput):
    ip: str
    scan_time: str
    ports: list[int]
    service_count: int


def lookup_host(
    params: GetHostActionParams, asset: Asset, soar: SOARClient[GetHostActionSummary]
) -> GetHostActionOutput:
    """
    Retrieves a host by its IP address
    """
    if not is_valid_ip(params.ip):
        return ActionResult(
            False,
            "Please provide a valid IPv4/IPv6 value in the 'ip' action parameter",
            dict(params),
        )

    if params.at_time is not None and not is_valid_at_time(params.at_time):
        return ActionResult(
            False,
            "Please provide a valid ISO 8601 timestamp in the 'at_time' action parameter, or leave it unset",
            dict(params),
        )

    logger.info(
        f"Loading host with IP {params.ip} (at_time: {params.at_time if params.at_time is not None else 'unspecified'})"
    )
    data: models.Host | None = None

    with create_censys_sdk(asset) as sdk:
        try:
            res = sdk.global_data.get_host(
                host_id=params.ip,
                at_time=str(params.at_time) if params.at_time else None,
            )
            data = res.result.result.resource
            logger.debug("Successfully retrieved host")
        except models.SDKBaseError as err:
            logger.error(err)
            raise ActionFailure(
                f"Failed to retrieve host with status code: {err.status_code}"
            ) from err
        except Exception as err:
            logger.error(err)
            raise ActionFailure("Failed to retrieve host with generic error") from err

    latest_scan = get_last_scanned_at(data)

    soar.set_summary(
        GetHostActionSummary(
            ip=data.ip,
            ports=[s.port for s in data.services],
            scan_time=latest_scan,
            service_count=data.service_count,
        )
    )
    soar.set_message(
        f"Host '{data.ip}' has {data.service_count:,} visible service(s), last scanned at {latest_scan}"
    )

    return GetHostActionOutput(scan_time=latest_scan, host=data)


def get_last_scanned_at(host: models.Host) -> str:
    return max(s.scan_time for s in host.services)
