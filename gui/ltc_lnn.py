import torch.nn as nn
from torch import tensor, no_grad, load, sigmoid
import numpy as np
from ncps.torch import LTC, CfC
from ncps.wirings import AutoNCP

RAND_SEED = 5904

# TODO move this file into proper location and change import accordingly
def init_weights(module):
    if isinstance(module, nn.Linear):
        nn.init.kaiming_normal_(module.weight, nonlinearity="leaky_relu")

        if module.bias is not None:
            nn.init.constant_(module.bias, 0)

class ProbabilityPredictor(nn.Module):
    def __init__(self, input_size, num_neurons, wiring : AutoNCP, lnn_type = "LTC", batch_first=True, return_sequences=True, ode_unfolds=6):
        super(ProbabilityPredictor, self).__init__()

        self.num_neurons = num_neurons
        self.lnn_type = lnn_type

        if self.lnn_type == "LTC":
            print("Using LTC LNN")
            self.ltc_lnn = LTC(input_size=input_size,
                                units=wiring,
                                batch_first=batch_first,
                                return_sequences=return_sequences,
                                ode_unfolds=ode_unfolds)

        elif self.lnn_type == "CFC":
            print("Using CFC LNN")
            self.cfc_lnn = CfC(input_size=input_size,
                            units=wiring,
                            batch_first=batch_first,
                            return_sequences=return_sequences)
        
        else:
            raise ValueError("lnn_type must be CFC or LTC")

        self.dropout1 = nn.Dropout(0.5)
        self.dropout2 = nn.Dropout(0.5)

        self.fc1 = nn.Linear(wiring.output_dim, int(wiring.output_dim * 2))
        self.normlayer1 = nn.LayerNorm(int(wiring.output_dim * 2))

        self.fc2 = nn.Linear(int(wiring.output_dim * 2), wiring.output_dim)
        self.normlayer2 = nn.LayerNorm(wiring.output_dim)

        self.fc3 = nn.Linear(wiring.output_dim, 1)

        self.leakyRelu = nn.LeakyReLU()
        self.apply(init_weights)

    def forward(self, input, timespans=None):

        if self.lnn_type == "LTC":
            x, _ = self.ltc_lnn(input=input, hx=None, timespans=timespans)

        elif self.lnn_type == "CFC":
            x, _ = self.cfc_lnn(input=input, hx=None, timespans=timespans)

        # skip1 = x

        x = self.fc1(x)
        x = self.normlayer1(x)
        x = self.leakyRelu(x)
        x = self.dropout1(x)
        
        # x = x + skip1

        # skip2 = x

        x = self.fc2(x)
        x = self.normlayer2(x)
        x = self.leakyRelu(x)
        x = self.dropout2(x)

        # x = x + skip1

        output = self.fc3(x)

        return output

def get_model(num_inputs, num_outputs, num_neurons, lnn_type="LTC", network_sparsity=0.5, ode_unfolds=6, return_sequences=True):
    
    network_wiring = AutoNCP(num_neurons, num_outputs, sparsity_level=network_sparsity, seed=RAND_SEED)

    model = ProbabilityPredictor(input_size=num_inputs,
                                    num_neurons=num_neurons,
                                    wiring=network_wiring,
                                    lnn_type=lnn_type,
                                    batch_first=True,
                                    return_sequences=return_sequences,
                                    ode_unfolds=ode_unfolds)
    return model

def load_ltc_weights(model : ProbabilityPredictor):
    state_dict = load("../models/weights_LTC.pth", weights_only=True)
    model.load_state_dict(state_dict)
    
def get_single_ltc_prediction( model : ProbabilityPredictor, feature_vector, time_length, time_steps):
    time_diff = float(time_length) / float(time_steps)

    timespans_list = [time_diff] * time_steps

    # Convert to numpy array
    single_test_t = np.stack(timespans_list)

    single_test_t = np.expand_dims(single_test_t, axis=-1)
    single_test_t = np.broadcast_to(single_test_t, (single_test_t.shape[0], model.num_neurons))
    single_test_t = tensor(single_test_t).float().unsqueeze(0)

    copied_vectors = [feature_vector.reshape(-1)] * time_steps
    single_test_X = np.stack(copied_vectors, axis=0)
    single_test_X = tensor(single_test_X).float().unsqueeze(0)

    with no_grad():
        model.to("cpu")
        model.eval()

        model.ltc_lnn.return_sequences = True
        pred = model(input=single_test_X, timespans=single_test_t)
        pred = sigmoid(pred)
        model.ltc_lnn.return_sequences = False

    pred_flatten = pred.reshape(-1).numpy()

    return pred_flatten