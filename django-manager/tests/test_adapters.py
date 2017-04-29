"""
These tests don't check the validity of the ViewSet or of the
Serializer but only assert that the ``python-cash-register``
integration works properly.
"""
import pytest

from django.utils import timezone

from serial import SerialException

from model_mommy import mommy

from registers import adapters
from registers.models import Product, Receipt, Sell
from registers.exceptions import AdapterPushFailed
from registers.adapters.services import DatadogAdapter
from registers.adapters.printers import CashRegisterAdapter


class TestCashRegisterAdapter:
    @pytest.mark.django_db
    def test_cash_register_adapter(self, mocker):
        """
        Ensure that a list of sold items is printed:
            * prepare a payload with 2 sold items
            * push the adapter
            * expect that the receipt is printed
        """
        # initialize the adapter
        adapter = CashRegisterAdapter()
        # spy third party libraries and mock the serial port
        mocker.patch('registers.adapters.printers.Serial')
        sell_products = mocker.spy(adapters.printers.SaremaX1, 'sell_products')
        send = mocker.spy(adapters.printers.SaremaX1, 'send')
        # sold products
        sold_items = [
            {
                'description': 'Croissant',
                'price': '5.90',
            },
            {
                'description': 'Begel',
                'price': '2.00',
                'quantity': '2.00',
            },
        ]
        # push data
        adapter.push(sold_items)
        assert sell_products.call_count == 1
        assert send.call_count == 1

    @pytest.mark.django_db
    def test_cash_register_adapter_failure(self, mocker):
        """
        Ensure that an AdapterPushFailed is raised when using this
        adapter:
            * prepare a payload with 2 sold items
            * push the adapter
            * expect that an exception is raised
        """
        # initialize the adapter
        adapter = CashRegisterAdapter()
        # mock the serial port so that it raises an Exception
        serial_port = mocker.patch('registers.adapters.printers.Serial')
        serial_port.side_effect = SerialException
        # sold products
        sold_items = [
            {
                'description': 'Croissant',
                'price': '5.90',
            },
            {
                'description': 'Begel',
                'price': '2.00',
                'quantity': '2.00',
            },
        ]
        # push data and check the Exception
        with pytest.raises(AdapterPushFailed) as excinfo:
            adapter.push(sold_items)
        assert excinfo.typename == 'CashRegisterNotReady'


class TestDatadogAdapter:
    def setup(self):
        # initialize the adapter
        self.adapter = DatadogAdapter()

    def tearDown(self):
        self.adapter.statsd.stop()

    def test_adapter_initialization(self):
        """
        Ensures that the adapter initializes a statsd server:
            * the Adapter is initialized
            * the statsd server is created at init time
            * the flushing thread is not active because the API_KEY is not set
        """
        assert self.adapter.statsd._disabled is True

    def test_adapter_enabled_with_api_key(self, settings):
        """
        Ensures that the statsd server is enabled if an API_KEY
        is not provided:
            * the Adapter is initialized
            * the statsd server is created at init time
            * the flushing thread must be active
        """
        try:
            # the Datadog API_KEY is set
            settings.DATADOG_API_KEY = 'testing-key'

            # start the statsd thread that should remain disabled
            adapter = DatadogAdapter()
            assert adapter.statsd._disabled is False
        finally:
            adapter.statsd.stop()

    @pytest.mark.django_db
    def test_flushing_thread(self, mocker):
        """
        Ensures that the statsd server flushes metrics when the adapter
        is invoked:
            * a `Receipt` is created
            * the flushing thread must send many metrics
        """
        # set spies
        increment = mocker.spy(self.adapter.statsd, 'increment')

        # create a receipt
        product = mommy.make(Product, default_price=2.50)
        receipt = mommy.make(Receipt)
        # update the receipt auto_now_add attribute
        new_time = timezone.datetime(2016, 1, 1)
        receipt.date = new_time
        receipt.save()
        # add Sell items
        Sell.objects.create(
            receipt=receipt,
            product=product,
            quantity=1,
            price=1.0,
        )
        # test the adapter
        self.adapter.push(receipt)
        assert increment.call_count == 3
        # receipt count metric
        args, kwargs = increment.call_args_list[0]
        assert args[0] == 'shop.shop.receipt.count'
        assert kwargs['timestamp'] == 1451606400.0
        # items count metric
        args, kwargs = increment.call_args_list[1]
        assert args[0] == 'shop.shop.receipt.items.count'
        assert 'product:' in kwargs['tags'][0]
        assert kwargs['timestamp'] == 1451606400.0
        assert kwargs['value'] == 1.0
        # items amount metric
        args, kwargs = increment.call_args_list[2]
        assert args[0] == 'shop.shop.receipt.amount'
        assert 'product:' in kwargs['tags'][0]
        assert kwargs['timestamp'] == 1451606400.0
        assert kwargs['value'] == 1.0

    def test_flushing_thread_exception(self, mocker):
        """
        Ensures that the flushing thread raises an exception
        if something goes wrong:
            * a `Receipt` is created
            * the flushing thread raises an error because of an issue
        """
        # set mocks
        mocker.patch('registers.adapters.services.ThreadStats')
        adapter = DatadogAdapter()
        adapter.statsd.increment.side_effect = Exception
        # push data and check the Exception
        with pytest.raises(AdapterPushFailed) as excinfo:
            adapter.push(Receipt())
        assert excinfo.typename == 'AdapterPushFailed'
