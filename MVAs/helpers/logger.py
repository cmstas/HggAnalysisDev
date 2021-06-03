import numpy

class Logger():
    def __init__(self, early_stopping_epochs):
        self.train_loss = []  # 2D array
        self.val_loss = []  # 1D array
        self.check_early_stopping = False
        self.early_stopping_epochs = -1
        if early_stopping_epochs > 0:
            self.check_early_stopping = True
            self.early_stopping_epochs = early_stopping_epochs

    def update_train_loss(self, epoch, batch_num, loss, verbosity=False):
        if batch_num == 0:
            if epoch > 0:
                self.train_loss.append(self.epoch_training_loss)
            self.epoch_training_loss = [loss]
        else:
            self.epoch_training_loss.append(loss)
        if verbosity:
            print("Epoch = {} batch number = {} training loss = {}".format(epoch, batch_num, loss))

    def update_val_loss(self, epoch, loss, verbosity=False):
        self.val_loss.append(loss)
        if verbosity:
            print("Epoch = {} validation loss = {}".format(epoch, loss))

        # check for early stopping
        if self.check_early_stopping and len(self.val_loss) >= self.early_stopping_epochs:
            if all(numpy.sort(self.val_loss[-self.early_stopping_epochs:]) == self.val_loss[-self.early_stopping_epochs:]):
                return True
            else:
                return False
        else:
            return False

    def save_losses(self, output_tag):
        numpy.savetxt("output/{}_val_loss.txt".format(output_tag), self.val_loss)
        numpy.savetxt("output/{}_train_loss.txt".format(output_tag), self.train_loss)
