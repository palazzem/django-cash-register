class BaseAdapter(object):
    """
    BaseAdapter provides the interface that must be honored when
    creating a new Adapter. This is used to add external integrations
    when a receipt model is saved, pushing data to a third-party
    component like a printer or a web service.
    """
    def push(self, items):
        """
        Push method is called when the serializer or the Django admin
        stores data in the selected database. This method MUST be
        implemented for any used `Adapter`.
        """
        raise NotImplementedError
