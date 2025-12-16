from soar_sdk.app import App

from .lookup_cert import lookup_cert
from .lookup_host import lookup_host, lookup_host_view_handler
from .lookup_web_property import lookup_web_property
from .search import search


def register_all_actions(app: App) -> None:
    app.register_action(
        lookup_cert,
        render_as="json",
        verbose="Retrieve a certificate by SHA256 fingerprint from the Censys Platform API",
    )
    app.register_action(
        lookup_host,
        view_handler=lookup_host_view_handler,
        view_template="lookup_host.html",
        verbose="Retrieve a host by IP address from the Censys Platform API",
    )
    app.register_action(
        lookup_web_property,
        render_as="json",
        verbose="Retrieve a web property by domain_name:port from the Censys Platform API",
    )
    app.register_action(
        search,
        render_as="json",
        verbose="Searches across all Censys assets using the provided CenQL query",
    )
