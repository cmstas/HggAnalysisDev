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

    def fit(self):
        self.prepare_data()
        self.prepare_models()
        self.fit_models()

    def prepare_data(self):
        self.obs = zfit.Space('mgg', (100, 180))
        self.zdata = zfit.Data.from_pandas(
            obs = self.obs,
            df = self.data["gg_mass"],
            weights = self.data["weight"]
        )
        return

    def prepare_models(self):
        self.parameters = []
        self.models = []

        for pdf in self.pdfs: # can supply multiple pdfs to fit
            parameters, model = self.prepare_model(pdf)

        return

    def prepare_model(self, name):
        parameters = []
        if name == "gaussian":
            parameters.append(zfit.Parameter('mu', 125, 122, 128, step_size = 0.25))
            parameters.append(zfit.Parameter('sigma', 2, 0.5, 3.0, step_size = 0.25))

            model = zfit.pdf.Gauss(
                obs = self.obs,
                mu = parameters[0],
                sigma = parameters[1]
            )

        else:
            print("[model_helper.py : prepare_model] PDF %s not implemented" % name)
            return None

        return parameters, model

