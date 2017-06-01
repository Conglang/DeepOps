# Deep Ops
Code challenges for Siraj's [Intro to Deep Learning](https://www.youtube.com/playlist?list=PL2-dafEMk2A7YdKv4XfKpfbTH5z6rEEj3) Series.

## Op1_simple_linear_regression
Code challenge for [How to Make a Prediction - Intro to Deep Learning #1](https://www.youtube.com/watch?v=vOppzHpvTiQ&list=PL2-dafEMk2A7YdKv4XfKpfbTH5z6rEEj3&index=1).
> The challenge for this video is to use scikit-learn to create a line of best fit for the included 'challenge_dataset'. Then, make a prediction for an existing data point and see how close it matches up to the actual value. Print out the error you get.

## Op2_make_3layer_neural_network
Code challenge for [How to Make a Neural Network - Intro to Deep Learning #2](https://www.youtube.com/watch?v=p69khggr1Jo&list=PL2-dafEMk2A7YdKv4XfKpfbTH5z6rEEj3&index=3).

Ref: ludobouan's [pure-numpy-feedfowardNN](https://github.com/ludobouan/pure-numpy-feedfowardNN).
> The challenge for this video is to create a 3 layer feedforward neural network using only numpy as your dependency.

## Op3_sentiment_analysis_of_game_reviews
Code challenge for [How to Do Sentiment Analysis - Intro to Deep Learning #3](https://www.youtube.com/watch?v=si8zZHkufRY&list=PL2-dafEMk2A7YdKv4XfKpfbTH5z6rEEj3&index=5).

Ref: jovianlin's [siraj-intro-to-DL-03](https://github.com/jovianlin/siraj-intro-to-DL-03).
> The challenge for this video is to train a model on [this](https://www.kaggle.com/egrinstein/20-years-of-games) dataset of video game reviews from IGN.com. Then, given some new video game title it should be able to classify it. You can use pandas to parse this dataset. Right now each review has a label that's either Amazing, Great, Good, Mediocre, painful, or awful. These are the emotions. Using the existing labels is extra credit. The baseline is that you can just convert the labels so that there are only 2 emotions (positive or negative). Ideally you can use an RNN via TFLearn like the one in this example, but I'll accept other types of ML models as well.

## Op4_predict_magnitude_of_earthquake
Code Challenge for [How to Do Mathematics Easily](https://www.youtube.com/watch?v=N4gDikiec8E&list=PL2-dafEMk2A7YdKv4XfKpfbTH5z6rEEj3&index=7).

Ref: https://www.kaggle.com/artimous/d/usgs/earthquake-database/visualizing-earthquakes-via-animations
[Numpy Only Version](https://github.com/alkaya/earthquake-cotw) by alkaya.

> The challenge for this video is to build a neural network to predict the magnitude of an Earthquake given the date, time, Latitude, and Longitude as features. [This](https://www.kaggle.com/usgs/earthquake-database) is the dataset. Optimize at least 1 hyperparameter using Random Search. See [this](http://scikit-learn.org/stable/auto_examples/model_selection/randomized_search.html) example for more information.

## Op5_predict_dating_match_numpy_only
Code Challenge for [How to Make Data Amazing](https://www.youtube.com/watch?v=koiTTim4M-s&list=PL2-dafEMk2A7YdKv4XfKpfbTH5z6rEEj3&index=9).

> The coding challenge for this video is to use [this](https://www.kaggle.com/annavictoria/speed-dating-experiment) speed dating dataset to predict if someone gets a match or not. This dataset is labeled so 1 means they got a match and 0 means they didn't. Build a neural network capable of predicting a match given a new person. You can use any library you like, bonus points if you do this from scratch using only numpy.