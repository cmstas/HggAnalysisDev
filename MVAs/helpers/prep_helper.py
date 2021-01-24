import h5py

class PrepHelper():
    """
    Class to read events in from an ntuple and perform necessary
    preprocessing, sample labeling, etc and then write them
    to an output hdf5 file to be used for BDT/DNN trainig
    """

    def __init__(self, **kwargs):
        self.input = kwargs.get("input")
        self.output_tag = kwargs.get("output_tag")
        self.debug = kwargs.get("debug")

        if self.debug > 0:
            print("[PrepHelper] Creating PrepHelper instance with options:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in kwargs.items()]))

    def run(self):
        return
