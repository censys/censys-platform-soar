from censys_platform import models

from ..utils import get_attr_path


def format_software(
    vendor: str | None, product: str | None, version: str | None
) -> str | None:
    vendor_str = (vendor or "").strip()
    product_str = (product or "").strip()
    version_str = (version or "").strip()

    if not product_str and not vendor_str:
        return None

    product_starts_with_vendor = (
        vendor_str
        and product_str
        and product_str.lower().startswith(vendor_str.lower())
    )

    parts = []
    if not product_starts_with_vendor and vendor_str:
        parts.append(vendor_str)
    if product_str:
        parts.append(product_str)
    if version_str:
        parts.append(version_str)

    software_name = " ".join(parts)

    formatted = software_name.replace("_", " ")
    formatted = " ".join(word.capitalize() for word in formatted.split())

    return formatted


def extract_cert_fields(cert: models.Certificate) -> dict:
    return {
        "fingerprint_sha256": getattr(cert, "fingerprint_sha256", None),
        "display_name": get_cert_display_name(cert),
        "subject_dn": get_attr_path(cert, "parsed.subject_dn", "N/A"),
        "issuer_dn": get_attr_path(cert, "parsed.issuer_dn", "N/A"),
        "common_names": _render_common_names(cert),
        "valid_from": get_attr_path(cert, "parsed.validity_period.not_before", "N/A"),
        "valid_to": get_attr_path(cert, "parsed.validity_period.not_after", "N/A"),
        "self_signed": _render_self_signed(cert),
    }


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

    return getattr(cert, "fingerprint_sha256", "N/A")


def _render_common_names(cert: models.Certificate) -> list[str]:
    common_names = get_attr_path(cert, "parsed.subject.common_name", [])
    if common_names and isinstance(common_names, list):
        return common_names
    return []


def _render_self_signed(cert: models.Certificate) -> str:
    self_signed = get_attr_path(cert, "parsed.signature.self_signed", None)
    if self_signed is True:
        return "Yes"
    elif self_signed is False:
        return "No"
    return "Unknown"
