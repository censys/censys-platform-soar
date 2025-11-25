from pydantic import Field
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.logging import getLogger
from soar_sdk.params import Params

from config import Asset

logger = getLogger()


class GetWebPropertyActionParams(Params):
    hostname: str
    port: int = Field(gte=1, lte=65535)


class GetWebPropertyActionOutput(ActionOutput):
    hostname: str = OutputField(
        cef_types=["dhost", "shost"],
        example_values=["server1.example.com"],
    )
    port: int = OutputField(
        cef_types=["cpt", "dpt"],
        example_values=[22, 443, 8080],
    )


def get_web_property(
    params: GetWebPropertyActionParams, asset: Asset
) -> GetWebPropertyActionOutput:
    """
    Retrieves a web property by domain_name:port
    """
    return GetWebPropertyActionOutput(hostname=params.hostname, port=params.port)
