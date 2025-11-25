from censys_platform import models
from pydantic import Field
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, ActionResult
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger
from soar_sdk.params import Params

from config import Asset
from utils import create_censys_sdk, is_valid_ip

logger = getLogger()


class GetHostActionParams(Params):
    ip: str = Field(description="IPv4/IPv6 address for the host to lookup")


class GetHostActionOutput(ActionOutput):
    host: models.Host


class GetHostActionSummary(ActionOutput):
    ip: str
    ports: list[int]
    service_count: int


def get_host(
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

    logger.info(f"Loading host with IP {params.ip}")
    data: models.Host | None = None

    with create_censys_sdk(asset) as sdk:
        try:
            res = sdk.global_data.get_host(host_id=params.ip)
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

    soar.set_summary(
        GetHostActionSummary(
            ip=data.ip,
            ports=[s.port for s in data.services],
            service_count=data.service_count,
        )
    )
    soar.set_message(f"Host '{data.ip}' has {data.service_count} visible service(s)")

    return GetHostActionOutput(host=data)
