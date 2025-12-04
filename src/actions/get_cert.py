from datetime import datetime, UTC

from censys_platform import models
from pydantic import Field
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger
from soar_sdk.params import Params

from config import Asset
from utils import create_censys_sdk

logger = getLogger()


class GetCertActionParams(Params):
    fingerprint_sha256: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"[\da-zA-Z]{64}",
        description="Hex SHA256 fingerprint for the certificate to lookup",
    )


class GetCertActionOutput(ActionOutput):
    display_name: str
    cert: models.Certificate


class GetCertActionSummary(ActionOutput):
    display_name: str
    fingerprint_sha256: str


def get_cert(
    params: GetCertActionParams, asset: Asset, soar: SOARClient[GetCertActionSummary]
) -> GetCertActionOutput:
    """
    Retrieves a certificate by its hex SHA256 fingerprint
    """
    logger.info(f"Loading cert with fingerprint {params.fingerprint_sha256}")
    data: models.Certificate | None = None

    with create_censys_sdk(asset) as sdk:
        try:
            res = sdk.global_data.get_certificate(
                certificate_id=params.fingerprint_sha256
            )
            data = res.result.result.resource
            logger.debug("Successfully retrieved cert")
        except models.SDKBaseError as err:
            logger.error(err)
            raise ActionFailure(
                f"Failed to retrieve cert with status code: {err.status_code}"
            ) from err
        except Exception as err:
            logger.error(err)
            raise ActionFailure("Failed to retrieve cert with generic error") from err

    display_name = get_cert_display_name(data)
    validity_period_message = get_cert_validity_message(data)
    self_signed_message = get_cert_self_signed_message(data)

    soar.set_summary(
        GetCertActionSummary(
            display_name=display_name,
            fingerprint_sha256=data.fingerprint_sha256,
        )
    )
    soar.set_message(
        f"Cert '{display_name}': {self_signed_message} and {validity_period_message}."
    )

    return GetCertActionOutput(
        cert=data,
        display_name=display_name,
    )


def get_cert_display_name(cert: models.Certificate) -> str | None:
    """
    Attempts to produce a human-readable name for a certificate in the same way as the Censys Platform.
    """
    try:
        common_names = cert.parsed.subject.common_name
    except AttributeError:
        common_names = None

    if common_names and len(common_names) > 0 and common_names[0]:
        return common_names[0]

    try:
        subject_dn = cert.parsed.subject_dn
    except AttributeError:
        subject_dn = None

    if subject_dn is not None:
        return subject_dn

    return cert.fingerprint_sha256


def get_cert_validity_message(cert: models.Certificate) -> str:
    now = datetime.now(UTC)
    try:
        is_within_validity_period = False
        not_before = cert.parsed.validity_period.not_before
        not_after = cert.parsed.validity_period.not_after
        validity_parts: list[str] = []

        if not_before is not None:
            validity_parts.append(not_before)
            is_within_validity_period = now > datetime.fromisoformat(not_before)
        else:
            validity_parts.append("*")

        if not_after is not None:
            validity_parts.append(not_after)
            is_within_validity_period = (
                is_within_validity_period and now < datetime.fromisoformat(not_after)
            )
        else:
            validity_parts.append("*")

        formatted_validity_parts = " - ".join(validity_parts)

        if is_within_validity_period:
            return f"is within its validity period [{formatted_validity_parts}]"

        return f"is not within its validity period [{formatted_validity_parts}]"
    except AttributeError:
        return "its validity period could not be determined"


def get_cert_self_signed_message(cert: models.Certificate) -> str:
    try:
        self_signed = cert.parsed.signature.self_signed
        if self_signed:
            return "is self-signed"
        else:
            return "is not self-signed"
    except AttributeError:
        return "we could not determine whether it is self-signed"
