from multiprocessing.pool import ThreadPool

from w2w_rome.helpers.errors import GotErrorInThreads


def run_in_threads(func, logger, param_map):
    """Run function in the threads.

    :type func: function
    :type logger: logging.Logger
    :param param_map: cli_service: [args_list, kwargs_dict]
    :type param_map: dict[cloudshell.cli.cli_service_impl.CliServiceImpl, list[list, dict]]
    :return: dict with cli_service: result
    :rtype: dict[cloudshell.cli.cli_service_impl.CliServiceImpl, str]
    """
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
            logger.exception(
                "Got exception on the host {}".format(cli_service.session.host)
            )

    if errors:
        raise GotErrorInThreads("Got exception on the host, look in the logs")

    return results_map
