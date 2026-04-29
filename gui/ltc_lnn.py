import torch.nn as nn
from torch import tensor, no_grad, load
import numpy as np
from ncps.torch import LTC
from ncps.wirings import AutoNCP

RAND_SEED = 5904

# TODO move this file into proper location and change import accordingly
class ProbabilityPredictorLTC(nn.Module):
    def __init__(self, input_size, num_neurons, wiring : AutoNCP, batch_first=True, return_sequences=False, ode_unfolds=6):
        super(ProbabilityPredictorLTC, self).__init__()
        
        self.num_neurons = num_neurons

        self.ltc_lnn = LTC(input_size=input_size,
                            units=wiring,
                            batch_first=batch_first,
                            return_sequences=return_sequences,
                            ode_unfolds=ode_unfolds)
        
        self.fc1 = nn.Linear(wiring.output_dim, 1)

        self.sigmoid = nn.Sigmoid()
    
    def forward(self, input, timespans):

        x, _ = self.ltc_lnn(input=input, hx=None, timespans=timespans)
        x = self.fc1(x)
        x = self.sigmoid(x)

        return x

def get_ltc_model(num_inputs, num_outputs, num_neurons, network_sparsity=0.5, ode_unfolds=6):
    
    network_wiring = AutoNCP(num_neurons, num_outputs, sparsity_level=network_sparsity, seed=RAND_SEED)

    model = ProbabilityPredictorLTC(input_size=num_inputs,
                                    num_neurons=num_neurons,
                                    wiring=network_wiring,
                                    batch_first=True,
                                    return_sequences=False,
                                    ode_unfolds=ode_unfolds)
    
    return model

def load_ltc_weights(model : ProbabilityPredictorLTC):
    state_dict = load("../models/weights_LTC.pth", weights_only=True)
    model.load_state_dict(state_dict)
    
def get_single_ltc_prediction( model : ProbabilityPredictorLTC, feature_vector, time_length, time_steps):
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
        model.ltc_lnn.return_sequences = False

    pred_flatten = pred.reshape(-1).numpy()

    return pred_flatten