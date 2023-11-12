from typing import Any
import numpy as np
import random
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits

###
# 2.1 Data
###

#load the dataset
digits = load_digits()

#extract into (input, target) tuples
#save "pixels"-array in "data"
data = digits.data
#save targets in "target"
target = digits.target
#zip the data and targets tuples into a list
data_tuples = list(zip(data, target))
#prints the type of the first elements in data and the first element itself
#print(type(data[0]), data[0][:])
#print()

'''
#prints the shape of data
print("Data shape: ", data.shape)
#prints the shape of our targets
print("Targets shape: ", target.shape)
print()
'''

#plot first 10 data images
fig, axes = plt.subplots(2, 5, figsize=(12, 6))
#go through the first tuples in data_tuples
for i, (image, t) in enumerate(data_tuples[:10]):
    #determine the row and column in plot
    ax = axes[i // 5, i % 5]
    #plot image
    ax.imshow(image.reshape(8, 8), cmap='gray')
    #show no axis
    ax.axis('off')


#images have the shape (64)
#print("Image shapes: ",np.shape(data))

#change type into float32 and reshape with maximum pixel value
data = data.astype(np.float32)
data = data / 16.0
#print("Data type: ", type(data[0][0]))

#onehot encoding target
targets = []
#interate through all target values
for j in target:
    #create a one-dimensional array of ten zeros
    one_hot_target = np.zeros(10) 
    #at idx j of one_hot_targets, replace 0.0 with 1.0
    one_hot_target[j] = 1.0
    #append to targets array
    targets.append(one_hot_target)
target = targets
#print("First target with one-hot encoding: ", target[0])

#zip tuples with data and one-hot-encoded target into a list
data_tuples = list(zip(data, target))

#generate minibatches
def batch_generator(data_tuples, minibatch_size):
    #shuffle the tuples in the data_tuples list
    random.shuffle(data_tuples)
    #determine the number of tuples
    num_samples = len(data_tuples)
    #determine the number of minibatches depending on the desired minibatch size
    num_minibatches = num_samples // minibatch_size 

    # for the number of minibatches, do:
    for i in range(num_minibatches):
        #determine start index
        start_idx = i * minibatch_size
        #determine end index
        end_idx = (i + 1) * minibatch_size
        #using the start and end index determine the tuples from data_tuples that will be in the minibatch
        minibatch_data = [data for data, target in data_tuples[start_idx:end_idx]]
        minibatch_target = [target for data, target in data_tuples[start_idx:end_idx]]

    return np.array(minibatch_data), np.array(minibatch_target)

'''
#create a minibatch - example

data = batch_generator(data_tuples, 5 )
print("data: ")
print()
#prints the inputs
print(data[0])
#prints the targets
print(data[1])  #gibt die targets aus
'''


###
# 2.2 Sigmoid Activation Function
###
class SigmoidActivation():
    def __init__(self):
        pass

    #actual sigmoid function
    def __call__(self,x):
        #save the input as self.input
        self.input = x
        #apply sigmoid function and return the solution
        return 1 / (1 + np.exp(-x))

'''
#example for sigmoid activation with a minibatch of size 5
sig_activate = SigmoidActivation()
print()
print("Sigmoid: ")
print(sig_activate(batch_generator(data_tuples, 5)[0]))
'''

###
# 2.3 Softmax Activation Function
###
class SoftmaxActivation():
    def __init__(self):
        pass

    #actual softmax activation function
    def __call__(self, x):

        softmax_output = []
        #get the size of the input vector - len(first elem in x) = 10, 
        #because there are 10 different digits
        size_input_vector = len(x[0])

        #iterate through every target vector
        for row in x:
            
            #calculate e^{z_i} for every element z_i in the current target vector
            row_exponents = np.exp(row)
            #calculate the sum of e^_{z_j} for j = 1,…,K with K=10 - so for all e^{z_i} elements in the target vector
            row_sum = np.sum(row_exponents, axis=-1, keepdims=True)
            
            #iterate through all elements in the current target vector
            for idx, elem in enumerate(row_exponents):
                #divide each e^{elem} be the sum of the vector
                row_exponents[idx] = row_exponents[idx]/row_sum
            
            #append converted vector to the softmax output array
            softmax_output.append(row_exponents)
        
        # Save the output for later use in backpropagation
        self.softmax_output = softmax_output  
        return softmax_output


#example for softmax activation
'''
soft_activate = SoftmaxActivation()

print()
print("Softmax:")
print(soft_activate(batch_generator(data_tuples, 5)[1]))
'''

###
# 2.4 MLP Layers and Weights
###

class MLP_layer():
    # input_size = number of units/perceptrons in the preceding layer
    # num_perceptrons = number of units/perceptrons in the given layer
    #def __init__(self, input_size, num_perceptrons, activation_func = "sigmoid", loc = 0.0, scale = 0.2):
    def __init__(self, input_size, num_perceptrons, loc = 0.0, scale = 0.2):
    
        #initialize weights as small, random, normally distributed values
        self.weights = np.random.normal(loc = loc, scale = scale, size = (input_size, num_perceptrons))
        #initialize the bias values set to zero
        self.bias = np.zeros((1, num_perceptrons))
        #self.activation_func = activation_func

    def call(self, input):
        #apply matrix multiplication and multiply the input and the weights
        #then add the bias
        #print("weights: ", self.weights)
        #print("input: ", input)
        output = np.matmul(input, self.weights) + self.bias
        
        '''
        # if the given layer is a hidden layer
        if self.activation_func == "sigmoid":
            #use sigmoid activation
            sigmoid = SigmoidActivation()
            output_sigm = sigmoid(output)
            return output_sigm
        
        #if the current layer is the final layer
        elif self.activation_func == "softmax":
            #use softmax activation
            softmax = SoftmaxActivation()
            output_softmax = softmax(output)
            return output_softmax
        '''
            


###
# 2.5 Putting together the MLP
###

class MLP():
    def __init__(self, input_size, sizes_hidden_layers, size_outputlayer):
        self.hidden_layers = []
        #iterate through all layers
        for layer_idx in range(len(sizes_hidden_layers)):
            #determine current input size
            #if we're not in the first layer, get size using sizes_hidden_layers[layer_idx - 1]
            #otherwise the current layer's input size is just the input size of the whole MLP
            current_input_size =  sizes_hidden_layers[layer_idx - 1] if layer_idx > 0 else input_size
            #for all hidden layers, append a MLP Layer to the hidden_layers list 
            self.hidden_layers = self.hidden_layers.append(MLP_layer(input_size = current_input_size, num_perceptrons = sizes_hidden_layers[layer_idx]))
        
        #for the final layer, the input size will be the last layer size from the hidden layer sizes array
        #and the number of perceptrons will be the given size of the output layer
        self.final_layer = MLP_layer(input_size = sizes_hidden_layers[-1], num_perceptrons = size_outputlayer)

        #define the activations
        self.sigmoid_activ = SigmoidActivation()    
        self.softmax_activ = SoftmaxActivation()
    
    def __call__(self, x):
        #for every single layer calculate the output and apply the sigmoid function to it
        for hidden_layer in self.hidden_layers:
            x = hidden_layer.call(x)
            x = self.sigmoid(x)
        
        #for the final layer, also compute the output and now use the softmax activation function
        x = self.final_layer(x)
        x = self.softmax_activ(x)
        return x


###
# 2.6 CCE loss function
###

class CCE_Loss():
    def __init_(self):
        pass

    #function input are the made predictions and the targets
    def loss_calculation(pred, target):
        #using the provided formula
        #calculate the cce loss
        prob = target * np.log(pred)
        cce_result = -1 * np.sum(prob, axis=1)
        return cce_result
    

