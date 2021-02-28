# bl-predictor <img src="https://www.python.org/static/community_logos/python-powered-w-70x28.png" alt="Python powered" align="right">  
<img src="https://raw.githubusercontent.com/lgehring/bl-predictor/master/bl-predictor_logo.svg" width="150" align="right">


[![Code quality](https://www.code-inspector.com/project/17966/score/svg)](https://frontend.code-inspector.com/public/project/17966/bl-predictor/dashboard) 
[![Coverage status](https://coveralls.io/repos/github/lgehring/bl-predictor/badge.svg)](https://coveralls.io/github/lgehring/bl-predictor) 
[![PyPI](https://img.shields.io/pypi/v/bl-predictor)](https://pypi.org/project/bl-predictor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.txt)  
[![pytest](https://github.com/lgehring/bl-predictor/workflows/pytest/badge.svg)](https://github.com/lgehring/bl-predictor/tree/main/tests) 
[![flake8](https://github.com/lgehring/bl-predictor/workflows/pep8/badge.svg)](https://www.python.org/dev/peps/pep-0008/)
[![CodeQL](https://github.com/lgehring/bl-predictor/workflows/CodeQL/badge.svg)](https://codeql.github.com/docs/codeql-overview/)
<br />
<span style="font-family:Helvetica; font-size:1em; font-weight:bold">  

Bl-predictor is a simple application for predicting game results for the German 1. Bundesliga.  
It features a clean graphical user interface (including DarkMode to spare your eyes), automatic data crawling, a variety of
prediction-models to choose from, and a few built-in model evaluation tools.
</span>

## Usage
#### Install:
```bash
pip install bl-predictor
```

#### and start the GUI:
```bash
bl-predictor-gui
```

The left column shows you the next upcoming matches. These are automatically crawled from [OpenligaDB](https://www.openligadb.de) when the application starts.  

The center column gives you the option to tweak your prediction preferences:
- choose the seasons used for training the model via the slider
- select a [model](#prediction-models) to train
- choose a home and guest team

Your result and additional information about the model used will appear in the righthand column.  
To make another prediction just use one of the reset-options on the bottom-left.

<center> <img src="https://media.giphy.com/media/nD4GGlxODQoGXUw5lJ/giphy.gif" alt="demo"/></center>  
  
You can switch to dark mode or exit the application under "Options" in the top-left corner.

<center> <img src="https://media.giphy.com/media/dQ8b4Lf5XasFzFpUEQ/giphy.gif" alt="dark mode"/></center>  

## Prediction models
#### PoissonModel
A model that predicts the winning team out of two given teams, based on a poisson regression model.  
**Caution:** The model is sensitive to the order of given teams, because the home_team scores better on average!
This model is heavily based on a [guideline from David Sheehan](https://dashee87.github.io/football/python/predicting-football-results-with-statistical-modelling/).
#### BettingPoissonModel
A adaptation of the PoissonModel improved for betting.  
If no relevant (>10%) difference in the teams winning probabilities is present, "Draw" is returned.
#### FrequencyModel
A model that uses all results of the last seasons to predict a winner based on the relative frequency of wins.

## Model Evaluation
The model evaluation features no graphical user interface.  
To access it you will need to go into the package source files to [prediction_evaluation.py](bl_predictor/prediction_evaluation.py)
and call the functions given at the bottom of the file. You can:
- generate a plot about the accuracy / F1-score of all models with different trainset sizes
- evaluate a single models performance 
  - trainset information
  - performance measures
  - ((Betting-)PoissonModel also returns a team-ranking based on the models coefficients)
- compare two models
- get general statistics about a trainset  

The results will either be given as printout in the console or as plots.png and will look something like this:

<a href="https://ibb.co/2d6dhHW"><img src="https://i.ibb.co/zZ5ZxDQ/Model-Evaluation.jpg" alt="Model-Evaluation" border="0"></a>

<center>
<a href="https://ibb.co/2YyFdws"><img src="https://i.ibb.co/Wp6HfQP/Poisson-Conf-Mat.png" alt="Poisson-Conf-Mat" border="0"></a>
</center>

<a href="https://imgbb.com/"><img src="https://i.ibb.co/X51FwxH/Model-Compare.jpg" alt="Model-Compare" border="0"></a>

<center>
<a href="https://ibb.co/CMH88xf"><img src="https://i.ibb.co/wwzggDf/Accuracy-over-time.png" alt="Accuracy-over-time" border="0"></a>
</center>  

## License
bl-predictor is made available under the [MIT-License](LICENSE.txt)  
