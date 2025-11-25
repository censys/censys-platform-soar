from pydantic import Field, IPvAnyAddress
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.logging import getLogger
from soar_sdk.params import Params

from config import Asset

logger = getLogger()


class GetHostActionParams(Params):
    ip: IPvAnyAddress


class GetHostActionOutput(ActionOutput):
    ip: IPvAnyAddress = OutputField(
        cef_types=["destinationAddress", "sourceAddress"],
        example_values=["8.8.8.8"],
    )


def get_host(params: GetHostActionParams, asset: Asset) -> ActionOutput:
    """
    Retrieves a host by its IP address
    """
    return GetHostActionOutput(ip=params.ip)


class GetCertActionParams(Params):
    fingerprint_sha256: str = Field(
        min_length=64, max_length=64, pattern=r"[\da-zA-Z]{64}"
    )


class GetCertActionOutput(ActionOutput):
    fingerprint_sha256: str = OutputField()


def get_cert(params: GetCertActionParams, asset: Asset) -> GetCertActionOutput:
    """
    Retrieves a certificate by its SHA256 fingerprint
    """
    return GetCertActionOutput(fingerprint_sha256=params.fingerprint_sha256)


class GetWebPropertyActionParams(Params):
    host: str
    port: int = Field(gte=1, lte=65535)


class GetWebPropertyActionOutput(ActionOutput):
    host: str = OutputField(
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
    return GetWebPropertyActionOutput(host=params.host, port=params.port)
