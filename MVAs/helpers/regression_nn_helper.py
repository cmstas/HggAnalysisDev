from tensorflow import keras
from tensorflow.keras import layers
import tensorflow
import numpy
import sys
from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from . import logger
from . import regression_model
import os

class NNHelper():
    def __init__(self, **kwargs):
        self.events = kwargs.get("events")
        self.config = kwargs.get("config")
        self.output_tag = kwargs.get("output_tag", "")
        self.debug = kwargs.get("debug")
        self.made_tensor = False

        if self.config is not None:
            self.config["mva"]["param"]["n_input"] = len(self.config["training_features"]) 
            self.model = regression_model.TauRegressionModel(self.config["mva"])
        else:
            self.model = None

    def train(self):
        # Old style - elaborate custom training loop
        if not self.made_tensor:
            self.make_tensor()
        if self.debug > 0:
            print("[DNNHelper] Training the following DNN")
            self.model.build(input_shape=(1,self.config["mva"]["param"]["n_input"])) 
            self.model.summary()
        n_max_epochs = self.config["mva"]["n_max_epochs"]
        if self.config["mva"]["early_stopping"]:
            n_early_stopping = self.config["mva"]["early_stopping_rounds"]
            print("[DNNHelper] Early stopping with {} rounds ({} maximum)".format(n_early_stopping, n_max_epochs))
        else:
            print("[DNNHelper] Training for {} (no early stopping)".format(n_max_epochs))
            n_early_stopping = -1
        optimizer = keras.optimizers.Adam(learning_rate=1e-3)
        logging = logger.Logger(n_early_stopping)
        # training happens here!
        for epoch in range(n_max_epochs):
            for step, (features, targets) in enumerate(self.events["train"]["tensor"]):
                with tensorflow.GradientTape() as tape:
                    outputs = self.model(features)
                    loss_value = loss_function(targets, outputs)
                    loss_value += tensorflow.add_n(self.model.losses)  # L2 addition happens here

                logging.update_train_loss(epoch, step, loss_value, (self.debug > 0))

                # do backprop to compute gradients
                gradients = tape.gradient(loss_value, self.model.trainable_weights)
                # do gradient descent
                optimizer.apply_gradients(zip(gradients, self.model.trainable_weights))

            # accuracy measure after every epoch
            validation_loss = 0
            val_dataset_length = 0
            for step, (features, targets) in enumerate(self.events["test"]["tensor"]):
                outputs = self.model(features)
                val_dataset_length += len(targets)
                validation_loss += loss_function(targets, outputs) * len(targets)
            validation_loss /= val_dataset_length
            
            # in addition to updating validation loss, this function will trigger the early stopping
            early_stop = logging.update_val_loss(epoch, validation_loss)
            if early_stop:
                print("Early stopping!")
                break

            # is this epoch the best one in terms of low validation loss1?
            if epoch == 0 or logging.best_epoch():
                self.save_model("best")
        logging.save_losses(self.output_tag)

    def compile_and_fit(self):
        # new style - keras does everything for me!
        callbacks = []
        if self.debug > 0:
            print("[DNNHelper] Training the following DNN")
            self.model.build(input_shape=(1,self.config["mva"]["param"]["n_input"])) 
            self.model.summary()
        n_max_epochs = self.config["mva"]["n_max_epochs"]
        if self.config["mva"]["early_stopping"]:
            n_early_stopping = self.config["mva"]["early_stopping_rounds"]
            print("[DNNHelper] Early stopping with {} rounds ({} maximum)".format(n_early_stopping, n_max_epochs))
            early_stopper = EarlyStopping(monitor="val_loss", patience=n_early_stopping, verbose=1)
            callbacks.append(early_stopper)
        else:
            print("[DNNHelper] Training for {} (no early stopping)".format(n_max_epochs))
            n_early_stopping = -1
              
        learning_rate = 5e-4
        if "learning_rate" in self.config["mva"].keys():
            learning_rate= self.config["mva"]["learning_rate"]
        if "loss" in self.config["mva"].keys() and self.config["mva"]["loss"] == "MSE":
            loss_function = keras.losses.MeanSquaredError()
        elif "loss" in self.config["mva"].keys() and self.config["mva"]["loss"] == "MAE":
            loss_function = keras.losses.MeanAbsoluteError()
        elif "loss" in self.config["mva"].keys() and self.config["mva"]["loss"] == "Huber":
            if "delta" in self.config["mva"].keys():            
                loss_function = keras.losses.Huber(delta=self.config["mva"]["delta"])
            else:
                loss_function = keras.losses.Huber()
        else:
            print("[DNNHelper] Cannot understand loss parameter {}. Defaulting to MSE".format(self.config["mva"]["error"]))
            loss_function = keras.losses.MeanSquaredError()

        optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
        
        reduce_learning_rate = False
        if "lr_reduction_factor" in self.config["mva"].keys():
            reduce_learning_rate = True
            lr_reducer = ReduceLROnPlateau(monitor="val_loss", factor=self.config["mva"]["lr_reduction_factor"], patience=5, verbose=1)
            callbacks.append(lr_reducer)
              
        # best model saving
        os.system("mkdir -p output/"+self.output_tag)

        best_checkpoint = ModelCheckpoint(filepath="output/{}/{}_model_best".format(self.output_tag, self.output_tag), save_weights_only=False, monitor="val_loss", mode="auto", save_best_only=True)
        # last model saving
        last_checkpoint = ModelCheckpoint(filepath="output/{}/".format(self.output_tag)+self.output_tag+"-weights-{epoch:02d}.hdf5", save_weights_only=True, monitor="val_loss", mode="auto", save_best_only=False)
        
        callbacks.extend([best_checkpoint, last_checkpoint])

        self.model.compile(optimizer=optimizer, loss=loss_function, metrics=[keras.metrics.MeanSquaredError(), keras.metrics.MeanAbsoluteError()])
        if "normalize_with_visible_tau_mass" in self.config.keys() and self.config["normalize_with_visible_tau_mass"]:
            history = self.model.fit(self.events["train"]["X"], self.events["train"]["y"], batch_size=1024, epochs=n_max_epochs, validation_data=(self.events["test"]["X"], self.events["test"]["y"]), callbacks=callbacks, shuffle=False)
        else:
            history = self.model.fit(self.events["train"]["X"], self.events["train"]["y"], batch_size=1024, epochs=n_max_epochs, validation_data=(self.events["test"]["X"], self.events["test"]["y"], self.events["test"]["weight"]), sample_weight=self.events["train"]["weight"], callbacks=callbacks, shuffle=False)
        numpy.savetxt("output/{}/{}_val_loss.txt".format(self.output_tag, self.output_tag), history.history["val_loss"])
        numpy.savetxt("output/{}/{}_train_loss.txt".format(self.output_tag, self.output_tag), history.history["loss"])

    def make_tensor(self, batch_size=128):
        for split in self.events.keys():
            x = self.events[split]["X"]
            y = self.events[split]["y"]
            if batch_size < 0:
                self.events[split]["tensor"] = tensorflow.data.Dataset.from_tensor_slices((x, y))
            else:
                self.events[split]["tensor"] = tensorflow.data.Dataset.from_tensor_slices((x, y)).batch(batch_size)
            self.made_tensor = True

    def predict_from_df(self, df, training_features=None):
        self.events = {}
        self.events["inference"] = {}
        if self.config is not None:
            training_features = self.config["training_features"]
        self.events["inference"]["tensor"] = tensorflow.data.Dataset.from_tensor_slices(df[training_features]).batch(1024)
        self.made_tensor = True
        return self.predict()

    def predict(self):
        """ For inference. Assumes fully loaded or trained model at disposal"""
        if not self.made_tensor:
            self.make_tensor()
        prediction = {}
        if "inference" in self.events.keys():
            splits = ["inference"]
        else:
            splits = ["test"]
        for split in splits:
            for step, features in enumerate(self.events[split]["tensor"]):
                print("step=",step)
                if type(features) is tuple:
                    features, targets = features
                if split not in prediction.keys():
                    prediction[split] = self.model(features).numpy().reshape(-1)
                else:
                    prediction[split] = numpy.append(prediction[split], self.model(features).numpy().reshape(-1))

        return prediction

    def save_model(self, model_tag=""):
        """ Save weights"""
        self.model.save("output/{}/{}_model_{}".format(self.output_tag, self.output_tag, model_tag))

    def load_model(self, model_tag=""):
        self.model = keras.models.load_model("output/{}/{}_model_{}".format(self.output_tag, self.output_tag, model_tag))

