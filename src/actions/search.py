from censys_platform import models
from pydantic import Field
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger
from soar_sdk.params import Param, Params

from config import Asset
from utils import create_censys_sdk

logger = getLogger()


class SearchActionParams(Params):
    query: str = Param(
        description="The CenQL search query to execute.",
    )
    page_size: int = Field(
        default=100,
        gte=0,
        required=False,
        description="The maximum number of results to include in each page.",
    )


class SearchActionOutput(ActionOutput):
    hits: list[models.SearchQueryHit]
    query_duration_millis: int
    total_hits: float


class SearchActionSummary(ActionOutput):
    query_duration_millis: int
    total_hits: float


def search(
    params: SearchActionParams, asset: Asset, soar: SOARClient[SearchActionSummary]
) -> SearchActionOutput:
    """
    Performs a search using the provided CenQL query string
    """
    logger.info(f"Performing search with page size {params.page_size}")
    data: models.SearchQueryResponse | None = None

    with create_censys_sdk(asset) as sdk:
        try:
            res = sdk.global_data.search(
                search_query_input_body=models.SearchQueryInputBody(
                    query=params.query, page_size=params.page_size
                )
            )
            data = res.result.result
            logger.debug("Successfully executed search")
        except models.SDKBaseError as err:
            logger.error(err)
            raise ActionFailure(
                f"Failed to execute search with status code: {err.status_code}"
            ) from err
        except Exception as err:
            logger.error(err)
            raise ActionFailure("Failed to execute search with generic error") from err

    soar.set_summary(
        SearchActionSummary(
            query_duration_millis=data.query_duration_millis, total_hits=data.total_hits
        )
    )
    soar.set_message(
        f"Search took {(data.query_duration_millis / 1000):.2n} seconds, found {int(data.total_hits):,} result(s)"
    )

    return SearchActionOutput(
        hits=data.hits,
        query_duration_millis=data.query_duration_millis,
        total_hits=data.total_hits,
    )
