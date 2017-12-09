import numpy as np
import sys

class NeuralNetwork():
    def __init__(self):
        np.random.seed(1)   # set random generator seed
        self.weights = {}   # hold weights
        self.biases = {}    # hold biases
        self.num_layers = 1 # initial layer is one (input layer)
    
    def add_layer(self, node_num, prev_node_num):
        # create weights and bias
        self.weights[self.num_layers] = np.random.normal(0.0, node_num**-0.5, (node_num, prev_node_num))
        self.biases[self.num_layers] = np.zeros(node_num)
        self.num_layers += 1

    def train(self, inputs, targets, num_epochs, learning_rate = 0.1):
        # for every epoch
        for it in range(num_epochs):
            loss = []
            weight_steps = {}
            bias_steps = {}
            # for every input
            for row in range(len(inputs)):
                x = inputs[row]
                y = targets[row]
                # forward propagation
                y_hat = self.__forward_propagate(x)
                loss.append(self.sum_squared_error(y_hat[self.num_layers], y))
                #print(y_hat[self.num_layers], y)
                # backword propagation
                single_weight_steps, single_bias_steps = self.__back_propagate(y_hat, y)

                for i in range(1, self.num_layers):
                    if i not in weight_steps:
                        weight_steps[i] = single_weight_steps[i]
                        bias_steps[i] = single_bias_steps[i]
                    else:
                        weight_steps[i] += single_weight_steps[i]
                        bias_steps[i] += single_bias_steps[i]
            
            sys.stdout.write("\rEpoch:" + str(it) + "   error:" + str(np.sum(loss)))
            # update weights
            self.__update_weights(len(inputs), weight_steps, bias_steps, learning_rate)
        print('')

    def predict(self, data):
        result = []
        for row in data:
            # pass through pretrained network
            for layer in range(2, self.num_layers):
                row = np.dot(row, self.weights[layer-1].T)
                row = np.add(row, self.biases[layer-1])
                row = self.__sigmoid(row)
            # output layer
            row = np.dot(row, self.weights[self.num_layers-1].T)
            row = np.add(row, self.biases[self.num_layers-1])
            result.append(row)
        return result

    def __sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def __sigmoid_derivative(self, x):
        return x * (1 - x)

    def __forward_propagate(self, data):
        # propagate through network and hold values for use in back-propagation
        output_values = {}
        output_values[1] = data
        for layer in range(2, self.num_layers):
            data = np.dot(data, self.weights[layer-1].T)
            data = np.add(data, self.biases[layer-1])
            data = self.__sigmoid(data)
            output_values[layer] = data
        # output layer
        data = np.dot(data, self.weights[self.num_layers-1].T)
        data = np.add(data, self.biases[self.num_layers-1])
        output_values[self.num_layers] = data
        return output_values

    def sum_squared_error(self, outputs, targets):
        return 0.5 * np.mean(np.sum(np.power(outputs - targets, 2)))

    def __back_propagate(self, output, target):
        deltas = {}
        weight_steps = {}
        bias_steps = {}
        # delta of output layer
        deltas[self.num_layers] = output[self.num_layers] - target
        bias_steps[self.num_layers-1] = output[self.num_layers] - target
        # delta of hidden layers (all layers except input/output)
        for layer in reversed(range(2, self.num_layers)):
            prev_delta = deltas[layer+1]
            weight = self.weights[layer]
            output_val = output[layer]
            deltas[layer] = np.multiply(np.dot(prev_delta, weight), self.__sigmoid_derivative(output_val))
            bias_steps[layer-1] = np.multiply(np.dot(prev_delta, weight), self.__sigmoid_derivative(output_val))
        # update weight steps
        for layer in range(1, self.num_layers):
            if layer not in weight_steps:
                weight_steps[layer] = np.dot(deltas[layer+1][:,None], output[layer][:,None].T)
            else:
                weight_steps[layer] += np.dot(deltas[layer+1][:,None], output[layer][:,None].T)
        return weight_steps, bias_steps

    def __update_weights(self, input_size, weight_steps, bias_steps, learning_rate):
        for layer in range(1, self.num_layers):
            self.weights[layer] += learning_rate * weight_steps[layer] / input_size * -1
            self.biases[layer] += learning_rate * bias_steps[layer] / input_size * -1

if __name__ == "__main__":
    # example usage, perform terribly
    # create instance of a neural network
    nn = NeuralNetwork()
    # add layers (input layer created by default)
    nn.add_layer(5, 3)
    nn.add_layer(2, 5)
    # training and testing data
    x_values = np.asarray([[1,1,1],[2,2,2],[3,3,3],[4,4,4],[5,5,5],[6,6,6],[7,7,7],[8,8,8],[9,9,9],[10,10,10],[11,11,11],[12,12,12]], dtype = np.float32).reshape(12,3)
    y_values = np.asarray([[2,1],[3,2],[4,3],[5,4],[6,5],[7,6],[8,7],[9,8],[10,9],[11,10],[12,11],[13,12]], dtype = np.float32).reshape(12,2)
    x_train = x_values[:7]
    y_train = y_values[:7]
    x_test = x_values[8:]
    y_test = y_values[8:]
    # train
    nn.train(x_train, y_train, 5000)
    y_hat_train = nn.predict(x_train)
    print('Training Error:  ', np.mean(nn.sum_squared_error(y_hat_train, y_train)))
    
    # predict
    y_hat = nn.predict(x_test)
    print('Testing Error:   ', np.mean(nn.sum_squared_error(y_hat, y_test)))
