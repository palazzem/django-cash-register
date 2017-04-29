import logging

from django.conf import settings

from datadog import initialize, ThreadStats

from .base import BaseAdapter
from .utils import slugify
from ..exceptions import AdapterPushFailed


logger = logging.getLogger(__name__)


class DatadogAdapter(BaseAdapter):
    """
    DatadogAdapter sends the given `Receipt` values to a local
    Datadog agent via dogstatsd.
    """
    METRIC_PREFIX = 'shop.{}'.format(slugify(settings.REGISTER_NAME))

    def __init__(self):
        # prepare the statsd client
        options = {
            'api_key': settings.DATADOG_API_KEY,
        }
        initialize(**options)

        # start the statsd thread
        disabled = not settings.DATADOG_API_KEY
        self.statsd = ThreadStats()
        self.statsd.start(flush_interval=1, roll_up_interval=1, disabled=disabled)
        logger.debug('statsd thread initialized, disabled: %s', disabled)

    def push(self, receipt):
        """
        Sends data to a local Datadog agent. The `Receipt` products
        are properly tagged using a stringify function so that
        they can be easily aggregated through Datadog backend.
        """
        try:
            # count the receipt
            timestamp = receipt.date.timestamp()
            count_metric = '{prefix}.receipt.count'.format(prefix=self.METRIC_PREFIX)
            self.statsd.increment(count_metric, timestamp=timestamp)

            for item in receipt.sell_set.all():
                # generate tags and metrics name
                tags = ['product:{}'.format(slugify(item.product.name))]
                items_count = '{prefix}.receipt.items.count'.format(prefix=self.METRIC_PREFIX)
                receipt_amount = '{prefix}.receipt.amount'.format(prefix=self.METRIC_PREFIX)

                # compute item metrics
                quantity = item.quantity
                total = float((item.price * item.quantity).amount)

                # send data
                self.statsd.increment(items_count, timestamp=timestamp, value=quantity, tags=tags)
                self.statsd.increment(receipt_amount, timestamp=timestamp, value=total, tags=tags)

            logger.debug('pushed metrics for %d sold items', receipt.sell_set.count())
        except Exception:
            raise AdapterPushFailed
