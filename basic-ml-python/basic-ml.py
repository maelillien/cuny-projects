'''
Basic ML
'''

# core
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ml
from sklearn import datasets as ds
from sklearn import linear_model as lm
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.model_selection import train_test_split as tts

# infra
import unittest


import plotly.graph_objects as go
import chart_studio
import chart_studio.plotly as py
username = 'maelillien' # chartstudio username
api_key = 'cYrDtxBdbpAj87FiVpTU' # chartstudio api_key
chart_studio.tools.set_credentials_file(username=username, api_key=api_key)


# Load datasets here once and assign to variables iris and boston
iris = ds.load_iris()
boston = ds.load_boston()

def exercise01():
    '''
        Data set: Iris
        Return the first 5 rows of the data including the feature names as column headings in a DataFrame and a
        separate Python list containing target names
    '''

    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df_first_five_rows = df.head(5)
    target_names = list(iris.target_names)

    return df_first_five_rows, target_names


def exercise02(new_observations):
    '''
        Data set: Iris
        Fit the Iris dataset into a kNN model with neighbors=5 and predict the category of observations passed in
        argument new_observations. Return back the target names of each prediction (and not their encoded values,
        i.e. return setosa instead of 0).
    '''

    X = iris.data
    y = iris.target

    knn = KNN(n_neighbors=5)    # Instantiate k-nn classifier with 5 neighbors
    knn.fit(X, y)               # Fit classifer to dataset
    # Predict and convert prediction values to labels
    iris_predictions = list(map((lambda x: iris.target_names[x]), knn.predict(new_observations)))

    return iris_predictions


def exercise03(neighbors, split):
    '''
        Data set: Iris
        Split the Iris dataset into a train / test model with the split ratio between the two established by
        the function parameter split.
        Fit KNN with the training data with number of neighbors equal to the function parameter neighbors
        Generate and return back an accuracy score using the test data was split out
    '''
    random_state = 21

    # Load and split data
    X = iris.data
    y = iris.target
    X_train, X_test, y_train, y_test = tts(X, y, test_size=split, random_state=random_state, stratify=y)

    knn = KNN(n_neighbors=neighbors)        # Setup k-NN Classifier with the neighbors parameter
    knn.fit(X_train, y_train)               # Fit classifier to the training data
    knn_score = knn.score(X_test, y_test)   # Score

    return knn_score


def exercise04():
    '''
        Data set: Iris
        Generate an overfitting / underfitting curve of kNN each of the testing and training accuracy performance scores series
        for a range of neighbor (k) values from 1 to 30 and plot the curves (number of neighbors is x-axis, performance score
        is y-axis on the chart). Return back the plotly url.
    '''

    # Setup arrays to store train and test accuracies
    neighbors = np.arange(1, 30)
    train_accuracy = np.empty(len(neighbors))
    test_accuracy = np.empty(len(neighbors))

    # Load and split the data, using test_size=0.3 and random_state=21 (not specified otherwise)
    X = iris.data
    y = iris.target
    X_train, X_test, y_train, y_test = tts(X, y, test_size=0.3, random_state=21, stratify=y)

    # Loop over values of k
    for i, k in enumerate(neighbors):

        knn = KNN(n_neighbors=k)                        # Setup k-NN Classifier with k neighbors
        knn.fit(X_train, y_train)                       # Fit the classifier to the training data
        train_accuracy[i] = knn.score(X_train, y_train) #  Compute accuracy on the training set
        test_accuracy[i] = knn.score(X_test, y_test)    # Compute accuracy on the testing set

    # Generate plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=neighbors, y=test_accuracy, mode='lines+markers', name='test accuracy'))
    fig.add_trace(go.Scatter(x=neighbors, y=train_accuracy, mode='lines+markers', name='train accuracy'))
    fig.update_layout(title='KNN Accuracy', xaxis_title='Number of neighbors', yaxis_title='Accuracy')
    # Return url and show plot
    plotly_overfit_underfit_curve_url = py.plot(fig, filename='knn_accuracy', auto_open=True)


    return plotly_overfit_underfit_curve_url


def exercise05():
    '''
        Data set: Boston
        Load sklearn's Boston data into a DataFrame (only the data and feature_name as column names)
        Load sklearn's Boston target values into a separate DataFrame
        Return back the average of AGE, average of the target (median value of homes or MEDV), and the target as NumPy values
    '''

    X = pd.DataFrame(boston.data, columns=boston.feature_names)
    y = pd.DataFrame(boston.target)

    average_age = X['AGE'].mean()
    average_medv= y.values.mean()
    medv_as_numpy_values = np.array(y)

    return average_age, average_medv, medv_as_numpy_values


def exercise06():
    '''
        Data set: Boston
        In the Boston dataset, the feature PTRATIO refers to pupil teacher ratio.
        Using a matplotlib scatter plot, plot MEDV median value of homes as y-axis and PTRATIO as x-axis
        Return back PTRATIO as a NumPy array
    '''

    X = pd.DataFrame(boston.data, columns=boston.feature_names)
    y = pd.DataFrame(boston.target)

    plt.scatter(X['PTRATIO'], y, alpha=0.5)
    plt.xlabel('PTRATIO')
    plt.ylabel('MEDV')
    plt.title('Pupil Teacher Ratio')

    X_ptratio = np.array(X['PTRATIO'])


    return X_ptratio


def exercise07():
    '''
        Data set: Boston
        Create a regression model for MEDV / PTRATIO and display a chart showing the regression line using matplotlib
        with a backdrop of a scatter plot of MEDV and PTRATIO from exercise06
        Use np.linspace() to generate prediction X values from min to max PTRATIO
        Return back the regression prediction space and regression predicted values
        Make sure to labels axes appropriately
    '''

    X_ptratio = exercise06().reshape(-1,1) # Load np.array from exercise 06
    y = boston.target.reshape(-1,1)

    reg = lm.LinearRegression() # Instantiate regression model
    reg.fit(X_ptratio, y)       # Fit to the training data
    prediction_space = np.linspace(min(X_ptratio), max(X_ptratio)).reshape(-1, 1)   # Create values for prediction
    reg_model = reg.predict(prediction_space)                                       # Predict
    plt.plot(prediction_space, reg_model, color='black', linewidth=2)               # Plot the regression trend line
    plt.show()                  # Activate exercise06 background plot and show trend line


    return reg_model, prediction_space


class TestBasicML(unittest.TestCase):
    def test_exercise07(self):
        rm, ps = exercise07()
        self.assertEqual(len(rm), 50)
        self.assertEqual(len(ps), 50)

    def test_exercise06(self):
        ptr = exercise06()
        self.assertTrue(len(ptr), 506)

    def test_exercise05(self):
        aa, am, mnpy = exercise05()
        self.assertAlmostEqual(aa, 68.57, 2)
        self.assertAlmostEqual(am, 22.53, 2)
        self.assertTrue(len(mnpy), 506)

    def test_exercise04(self):
        print('Skipping EX4 tests')

    def test_exercise03(self):
        score = exercise03(8, .25)
        self.assertAlmostEqual(exercise03(8, .3), .955, 2)
        self.assertAlmostEqual(exercise03(8, .25), .947, 2)

    def test_exercise02(self):
        pred = exercise02([[6.7, 3.1, 5.6, 2.4], [6.4, 1.8, 5.6, .2], [5.1, 3.8, 1.5, .3]])
        self.assertTrue('setosa' in pred)
        self.assertTrue('virginica' in pred)
        self.assertTrue('versicolor' in pred)
        self.assertEqual(len(pred), 3)

    def test_exercise01(self):
        df, tn = exercise01()
        self.assertEqual(df.shape, (5, 4))
        self.assertEqual(df.iloc[0, 1], 3.5)
        self.assertEqual(df.iloc[2, 3], .2)
        self.assertTrue('setosa' in tn)
        self.assertEqual(len(tn), 3)


if __name__ == '__main__':
    unittest.main()
