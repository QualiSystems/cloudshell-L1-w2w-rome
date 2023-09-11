from __future__ import annotations

from multiprocessing.pool import ThreadPool
from typing import TYPE_CHECKING, Callable

from cloudshell.layer_one.core.helper.logger import get_l1_logger
from w2w_rome.helpers.errors import GotErrorInThreads

if TYPE_CHECKING:
    from cloudshell.cli.service.cli_service_impl import CliServiceImpl

logger = get_l1_logger(name=__name__)


def run_in_threads(
    func: Callable, param_map: dict[CliServiceImpl, list[tuple[list, dict]]]
) -> dict[CliServiceImpl, str]:
    """Run function in the threads."""
    pool = ThreadPool(processes=len(param_map))
    async_results = {
        cli_service: pool.apply_async(func, args=args, kwds=kwargs)
        for cli_service, (args, kwargs) in param_map.items()
    }

    errors = []
    results_map = {}
    for cli_service, async_result in async_results.items():
        try:
            results_map[cli_service] = async_result.get()
        except Exception as e:
            errors.append(e)
            logger.exception(f"Got exception on the host {cli_service.session.host}")

    if errors:
        raise GotErrorInThreads("Got exception on the host, look in the logs")

    return results_map
