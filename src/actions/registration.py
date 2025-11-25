from soar_sdk.app import App

from .get_cert import get_cert
from .get_host import get_host
from .get_web_property import get_web_property


def register_all_actions(app: App) -> None:
    app.register_action(
        get_cert,
        name="Lookup Certificate",
        verbose="Retrieve a certificate by SHA256 fingerprint from the Censys Platform API",
        action_type="investigate",
    )
    app.register_action(
        get_host,
        name="Lookup Host",
        verbose="Retrieve a host by IP address from the Censys Platform API",
        action_type="investigate",
    )
    app.register_action(
        get_web_property,
        name="Lookup Web Property",
        verbose="Retrieve a web property by domain_name:port from the Censys Platform API",
        action_type="investigate",
    )
