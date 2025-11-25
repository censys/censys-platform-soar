from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.logging import getLogger
from soar_sdk.params import Params

from config import Asset

logger = getLogger()


class GetHostActionParams(Params):
    ip: str


class GetHostActionOutput(ActionOutput):
    ip: str = OutputField(
        cef_types=["destinationAddress", "sourceAddress"],
        example_values=["8.8.8.8"],
    )


def get_host(params: GetHostActionParams, asset: Asset) -> ActionOutput:
    """
    Retrieves a host by its IP address
    """
    return GetHostActionOutput(ip=params.ip)
