# -*- coding: utf-8 -*-
"""Stock Price Prediction Using Hidden Markov Model"""


# Install dependencies


pip install yfinance

pip install hmmlearn

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from hmmlearn.base import ConvergenceMonitor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
import itertools
from tqdm import tqdm
# %matplotlib inline



"""# Get Dataset"""

class PricePredictor:
  def __init__(self,n_hiden_states,train,test,n_steps_frac_change=50,n_steps_frac_high=10, n_steps_frac_low = 10,n_latency_days = 7,
               iterations = 100000,tol = 1e-8,verbose=True):
    self.n_latency_days = n_latency_days
    self.train = train
    self.test = test
    self.train_parameters = self.get_features(train)
    self.test_parameters = self.get_features(test)
    monitor = ConvergenceMonitor(tol=tol, n_iter=iterations, verbose=verbose)
    self.hmm = GaussianHMM(n_components=n_hiden_states,n_iter=iterations,covariance_type='diag')
    self.hmm.monitor_ = monitor
    self.all_possib(n_steps_frac_change, n_steps_frac_high, n_steps_frac_low)
  def fit(self):
    self.hmm.fit(self.train_parameters)
    print(self.hmm.monitor_.converged)

  def get_features(self,data):
    fraction_change = (data.Close - data.Open) / data.Open
    fraction_high = (data.High - data.Open) / data.Open
    fraction_low = (data.Open - data.Low) / data.Open
    return np.column_stack((fraction_change,fraction_high,fraction_low))


  def all_possib(self, n_steps_frac_change=50,
                                       n_steps_frac_high=10, n_steps_frac_low=10):
        frac_change_range = np.linspace(-0.1, 0.1, n_steps_frac_change)
        frac_high_range = np.linspace(0, 0.1, n_steps_frac_high)
        frac_low_range = np.linspace(0, 0.1, n_steps_frac_low)
        self.out = np.array((frac_change_range,frac_high_range,frac_low_range))
        self._possible_outcomes = np.array(list(itertools.product(
            frac_change_range, frac_high_range, frac_low_range)))

  def get_most_prob(self, day_index):
      previous_data_start_index = max(0, day_index - self.n_latency_days)
      previous_data_end_index = max(0, day_index - 1)
      previous_data = self.test.iloc[previous_data_end_index: previous_data_start_index]
      previous_data_features = self.get_features(previous_data)
      outcome_score = []
      for possible_outcome in self._possible_outcomes:
          total_data = np.row_stack((previous_data_features, possible_outcome))
          outcome_score.append(self.hmm.score(total_data))
      most_probable_outcome = self._possible_outcomes[np.argmax(
          outcome_score)]
      return most_probable_outcome

  def predict_close_price(self, day_index):
      open_price = self.test.iloc[day_index]['Open']
      predicted_frac_change, _, _ = self.get_most_prob(
          day_index)
      return open_price * (1 + predicted_frac_change)

model = PricePredictor(5,train,test)
model.fit()

predicted = np.array([])
real = np.array([])


for i in range(50,52):
  predicted = np.append(predicted, model.predict_close_price(i))
  real = np.append(real, model.test.iloc[i]["Close"])

model.test.iloc[0]

"""##FOR UNI"""

list_of_Download_Data = [1]

start_date = '2024-01-01'
end_date,end_data_test = '2024-02-01','2024-02-05'

DAYS_TO_PREDICT = 7
overall_predicted_precentage = np.array([])



for comp in list_of_Download_Data:
  train = yf.download("BTC-USD", start_date, end_date,interval='2m')
  test = yf.download("BTC-USD", end_date,end_data_test)
  model = PricePredictor(comp,train,test)
  model.fit()
  while(not (-0.00000001 < model.hmm.monitor_.history[-1]-model.hmm.monitor_.history[-2] < 0.00000004)):
    model.fit()
  predicted = np.array([])
  real = np.array([])
  for k in range(0,4):
    predicted = np.append(predicted, model.predict_close_price(k))
    real = np.append(real, model.test.iloc[k]["Close"])


  fig, ax = plt.subplots()
  ax.plot(real, 'bs-', label="prawdziwe dane")
  ax.plot(predicted, 'rs-', label="przewidywane dane")
  ax.set_title(f"Model with {comp} hiden state")
  ax.legend()
  fig.savefig(f"{comp}.png")

  fig, ax1 = plt.subplots()
  norm = abs(real/predicted -1)
  ax1.plot(norm,label="Loss")
  ax1.set_title(f"Model loss with {comp} hiden state")
  ax1.legend()
  fig.savefig(f"Loss_of_{comp}.png")
  real_d = np.where(real[1:] > real[:-1], 1, 0)
  p_d = np.where(predicted[1:] > predicted[:-1], 1, 0)
  score = accuracy_score(real_d,p_d)
  overall_predicted_precentage = np.append(overall_predicted_precentage,(comp,score))
  print(overall_predicted_precentage)

