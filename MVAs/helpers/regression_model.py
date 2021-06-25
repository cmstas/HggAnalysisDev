from tensorflow.keras import layers, Model, regularizers, initializers
import tensorflow
import sys


class TauRegressionModel(Model):
    def __init__(self, config):
        super(TauRegressionModel, self).__init__()

        n_hidden = config["param"]["n_hidden"]
        n_output = config["param"]["n_output"]
        n_input = config["param"]["n_input"]
        if "l2_lambda" in config["param"].keys():
            l2_lambda = config["param"]["l2_lambda"]
        else:
            l2_lambda = 0
        self.hidden_layers = []
        for i in range(1, n_hidden + 1):
            if "layer_{}".format(i) not in config.keys():
                print("Layer {} not found!".format(i))
                sys.exit(3)
            layer_info = config["layer_{}".format(i)]
            n_neurons = layer_info["n_neurons"]
            if "activation" not in layer_info.keys():
                activation = tensorflow.nn.relu
            elif layer_info["activation"] == "relu":
                activation = tensorflow.nn.relu
            elif layer_info["activation"] == "sigmoid":
                activation = tensorflow.nn.sigmoid

            if "l2_lambda" in layer_info.keys():
                l2_lambda = layer_info["l2_lambda"]

            self.hidden_layers.append(layers.Dense(n_neurons, activation=activation, name="layer_{}".format(i), kernel_regularizer=regularizers.l2(l2_lambda), kernel_initializer=initializers.GlorotNormal()))

        self.output_layer = layers.Dense(n_output, name="output", activation=tensorflow.nn.relu, kernel_regularizer=regularizers.l2(l2_lambda))

    def call(self, inputs):
        current_output = inputs
        for i in range(len(self.hidden_layers)):
            current_output = self.hidden_layers[i](current_output)

        # output
        output = self.output_layer(current_output)

        return output
