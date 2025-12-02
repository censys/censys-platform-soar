from soar_sdk.app import App

from .lookup_cert import lookup_cert
from .lookup_host import lookup_host
from .lookup_web_property import lookup_web_property
from .search import search


def register_all_actions(app: App) -> None:
    app.register_action(
        lookup_cert,
        verbose="Retrieve a certificate by SHA256 fingerprint from the Censys Platform API",
    )
    app.register_action(
        lookup_host,
        verbose="Retrieve a host by IP address from the Censys Platform API",
    )
    app.register_action(
        lookup_web_property,
        verbose="Retrieve a web property by domain_name:port from the Censys Platform API",
    )
    app.register_action(
        search,
        verbose="Searches across all Censys assets using the provided CenQL query",
    )
