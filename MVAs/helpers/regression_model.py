from tensorflow.keras import layers
import tensorflow


class TauRegressionModel(layers.Layer):
    def __init__(self, config):
        super(TauRegressionModel, self).__init__()

        n_hidden = config["param"]["n_hidden"]
        n_output = config["param"]["n_output"]
        self.hidden_layers = []
        for i in range(1, n_hidden):
            layer_info = config["layer_{}".format(i)]
            n_neurons = layer_info["n_neurons"]
            if "activation" not in layer_info.keys():
                activation = tensorflow.nn.relu
            elif layer_info["activation"] == "relu":
                activation = tensorflow.nn.relu
            elif layer_info["activation"] == "sigmoid":
                activation = tensorflow.nn.sigmoid
            self.hidden_layers.append(layers.Dense(n_neurons, activation=activation,name="layer_{}".format(i)))
        self.output_layer = layers.Dense(n_output, name="output")

    def call(self, inputs):
        current_output = inputs
        for i in range(len(self.hidden_layers)):
            current_output = self.hidden_layers[i](current_output)

        # output
        output = self.output_layer(current_output)

        return output
