import logging
import logging.config


logging.basicConfig(level=logging.INFO,
                    force=True,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

log = logging.getLogger('default')
