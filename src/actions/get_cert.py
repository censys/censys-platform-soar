from pydantic import Field
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.logging import getLogger
from soar_sdk.params import Params

from config import Asset

logger = getLogger()


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
