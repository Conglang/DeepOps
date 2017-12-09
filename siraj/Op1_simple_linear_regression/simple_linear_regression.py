import pandas as pd
from sklearn import linear_model
import matplotlib.pyplot as plt
import math

# read data
dataframe = pd.read_table('challenge_dataset.txt', sep = ',', header = None, names = ['x', 'y'])
x_values = dataframe[['x']]
y_values = dataframe[['y']]

# train model on data
reg = linear_model.LinearRegression()
reg.fit(x_values, y_values)

# calulate error of a specific point
x, y = dataframe.iloc[5]
y_hat = reg.predict(x)[0][0]
error = math.fabs(y - y_hat)
print('Original Value: {:>7}    Predict Value: {:>10}   Error: {:>10}'.format(y, y_hat, error))

# visualize results
plt.scatter(x_values, y_values)
plt.plot(x_values, reg.predict(x_values))
plt.show()