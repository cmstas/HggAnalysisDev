import zfit
from zfit import z

class ModelHelper()
    """
    Class to take an mgg distribution & weights
    and fit this to a specified function
    """

    def __init__(self, **kwargs):
        self.data = kwargs.get("data")
        self.pdfs = kwargs.get("pdfs")
        self.debug = kwargs.get("debug")
        self.output_tag = kwargs.get("output_tag")
        self.options = kwargs.get("options", {})


