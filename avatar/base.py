import logging

def prepare_logging(args):
    base_level = logging.WARNING
    offset = (args.quiet - args.verbose) * 10
    log_level = base_level + offset
    log_level = max(logging.DEBUG, min(logging.CRITICAL, log_level))
    
    logging.basicConfig(
        level=log_level,
        format="[%(levelname)8s] %(message)s"
    )
