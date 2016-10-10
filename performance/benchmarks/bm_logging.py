
"""Script for testing the performance of logging simple messages.
"""

# Python imports
import io
import logging

# Third party imports
import six
from six.moves import xrange
import perf.text_runner

# A simple format for parametered logging
FORMAT = 'important: %s'
MESSAGE = 'some important information to be logged'


def truncate_stream(stream):
    stream.seek(0)
    stream.truncate()


def bench_silent(loops, logger, stream, check):
    truncate_stream(stream)

    # micro-optimization: use fast local variables
    m = MESSAGE
    range_it = xrange(loops)
    t0 = perf.perf_counter()

    for _ in range_it:
        # repeat 10 times
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)

    dt = perf.perf_counter() - t0

    if check and len(stream.getvalue()) != 0:
        raise ValueError("stream is expected to be empty")

    return dt


def bench_simple_output(loops, logger, stream, check):
    truncate_stream(stream)

    # micro-optimization: use fast local variables
    m = MESSAGE
    range_it = xrange(loops)
    t0 = perf.perf_counter()

    for _ in range_it:
        # repeat 10 times
        logger.warn(m)
        logger.warn(m)
        logger.warn(m)
        logger.warn(m)
        logger.warn(m)
        logger.warn(m)
        logger.warn(m)
        logger.warn(m)
        logger.warn(m)
        logger.warn(m)

    dt = perf.perf_counter() - t0

    if check:
        lines = stream.getvalue().splitlines()
        if len(lines) != loops * 10:
            raise ValueError("wrong number of lines")

    return dt


def bench_formatted_output(loops, logger, stream, check):
    truncate_stream(stream)

    # micro-optimization: use fast local variables
    fmt = FORMAT
    msg = MESSAGE
    range_it = xrange(loops)
    t0 = perf.perf_counter()

    for _ in range_it:
        # repeat 10 times
        logger.warn(fmt, msg)
        logger.warn(fmt, msg)
        logger.warn(fmt, msg)
        logger.warn(fmt, msg)
        logger.warn(fmt, msg)
        logger.warn(fmt, msg)
        logger.warn(fmt, msg)
        logger.warn(fmt, msg)
        logger.warn(fmt, msg)
        logger.warn(fmt, msg)

    dt = perf.perf_counter() - t0

    if check:
        lines = stream.getvalue().splitlines()
        if len(lines) != loops * 10:
            raise ValueError("wrong number of lines")

    return dt


def prepare_subprocess_args(runner, args):
    args.append(runner.args.benchmark)


BENCHMARKS = {
    "silent": bench_silent,
    "simple": bench_simple_output,
    "format": bench_formatted_output,
}


if __name__ == "__main__":
    runner = perf.text_runner.TextRunner(name='logging', inner_loops=10)
    runner.metadata['description'] = "Test the performance of logging."
    runner.prepare_subprocess_args = prepare_subprocess_args

    parser = runner.argparser
    parser.add_argument("benchmark", choices=sorted(BENCHMARKS))

    options = runner.parse_args()
    bench = options.benchmark
    runner.name += "_%s" % bench
    bench_func = BENCHMARKS[bench]

    # NOTE: StringIO performance will impact the results...
    if six.PY3:
        stream = io.StringIO()
    else:
        stream = io.BytesIO()

    handler = logging.StreamHandler(stream=stream)
    logger = logging.getLogger("benchlogger")
    logger.propagate = False
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

    # Only check loggers in worker processes
    runner.bench_sample_func(bench_func, logger, stream, runner.args.worker)
