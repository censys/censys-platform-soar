from censys_platform import models
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, ActionResult
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger
from soar_sdk.params import Param, Params

from ..config import Asset
from ..utils import create_censys_sdk, get_attr_path, is_valid_at_time, is_valid_ip
from .action_output import CensysActionOutput

logger = getLogger()


class GetHostActionParams(Params):
    ip: str = Param(description="IPv4/IPv6 address for the host to lookup")
    at_time: str | None = Param(
        default=None,
        required=False,
        description="The historical timestamp to retrieve host data for. If unspecified, we will retrieve the latest data.",
    )


class GetHostActionOutput(CensysActionOutput):
    host: models.Host
    is_truncated_host: bool
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

    is_truncated_host = any(s.representative_info is not None for s in data.services)

    soar.set_summary(
        GetHostActionSummary(
            ip=data.ip,
            ports=list(set(getattr(s, "port", None) or 0 for s in data.services)),
            scan_time=latest_scan,
            service_count=getattr(data, "service_count", None) or len(data.services),
        )
    )

    if is_truncated_host:
        soar.set_message(
            f"Host '{data.ip}' has many visible services and has been truncated due to its size, last scanned at {latest_scan}"
        )
    else:
        soar.set_message(
            f"Host '{data.ip}' has {data.service_count:,} visible service(s), last scanned at {latest_scan}"
        )

    return GetHostActionOutput(
        scan_time=latest_scan, is_truncated_host=is_truncated_host, host=data
    )


def get_last_scanned_at(host: models.Host) -> str:
    return max(s.scan_time for s in host.services)


def lookup_host_view_handler(all_outputs: list[GetHostActionOutput]) -> dict:
    return {
        "results": [
            {
                "ip": output.host.ip,
                "scan_time": output.scan_time,
                "is_truncated": getattr(output, "is_truncated_host", False),
                "reverse_dns": get_attr_path(output, "host.dns.reverse_dns.names", []),
                "whois_name": get_attr_path(output, "host.whois.network.name", "N/A"),
                "whois_cidr": get_attr_path(output, "host.whois.network.cidrs", []),
                "asn": render_asn(output),
                "services": render_services(output),
                "labels": render_labels(output),
                "threats": render_threats(output),
                "location": render_location(output),
            }
            for output in all_outputs
        ],
        "total_count": len(all_outputs),
    }


def render_asn(output: GetHostActionOutput) -> str:
    name = get_attr_path(output, "host.autonomous_system.name")
    asn = get_attr_path(output, "host.autonomous_system.asn")

    if not name or not asn:
        return "N/A"

    return f"{name} ({asn})"


def render_services(output: GetHostActionOutput) -> list[dict]:
    return [
        {
            "port": svc.port,
            "protocol": svc.protocol,
            "transport_protocol": svc.transport_protocol.value.upper(),
        }
        for svc in get_attr_path(output, "host.services", [])
    ]


def render_labels(output: GetHostActionOutput) -> list[str]:
    labels = set[str]()

    for label in get_attr_path(output, "host.labels", []):
        labels.add(label.value)

    for svc in get_attr_path(output, "host.services", []):
        for label in getattr(svc, "labels", []):
            labels.add(label.value)

    return list(labels)


def render_threats(output: GetHostActionOutput) -> list[str]:
    threats = set[str]()

    for svc in get_attr_path(output, "host.services", []):
        for threat in getattr(svc, "threats", []):
            threats.add(threat.name)

    return list(threats)


def render_location(output: GetHostActionOutput) -> dict:
    return {
        "city": get_attr_path(output, "host.location.city", None),
        "country": get_attr_path(output, "host.location.country", None),
        "country_code": get_attr_path(output, "host.location.country_code", None),
        "continent": get_attr_path(output, "host.location.continent", None),
        "postal_code": get_attr_path(output, "host.location.postal_code", None),
        "province": get_attr_path(output, "host.location.province", None),
        "latitude": get_attr_path(output, "host.location.coordinates.latitude", None),
        "longitude": get_attr_path(output, "host.location.coordinates.longitude", None),
    }
