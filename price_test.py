import os
from optparse import OptionParser

# local imports
from price_feeder import PriceFeeder

if __name__ == '__main__':

    usage = '%prog [options] '
    parser = OptionParser(usage=usage)

    parser.add_option('-n', '--network', action='store', dest='network', type="string", help='network')

    parser.add_option('-c', '--config', action='store', dest='config', type="string", help='config')

    parser.add_option('-b', '--build', action='store', dest='build', type="string", help='build')

    parser.add_option('-t', '--test_only', action='store_true', dest='test_only', help='Make some test')

    (options, args) = parser.parse_args()

    if not options.config:
        config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
    else:
        config_path = options.config

    if not options.network:
        network = 'local'
    else:
        network = options.network

    if not options.build:
        build_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'build')
    else:
        build_dir = options.build

    price_feeder = PriceFeeder(config_path, network, build_dir)

    if options.test_only:
        # make some test only
        pass
    else:
        # only fetch price
        price_feeder.job_ponderated_price()


