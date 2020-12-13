"""
This module contains the GUI code.
"""

import datetime
from datetime import date
import inspect
import tkinter as tk

import pandas as pd

from teamproject import models
from teamproject.crawler import fetch_data
from teamproject.gui_slider_widget import Slider


class MainWindow:
    """
    Graphical User Interface for the bl-predictor project.

    The GUI window can be shown with show_window()
    """

    def __init__(self):
        self.root = tk.Tk()

        self.crawler_data = pd.DataFrame()
        self.picked_home_team = None
        self.picked_guest_team = None

    def show_window(self):
        """
        Shows the bl-predictor GUI.

        Options to choose
        a timeframe for data-crawling,
        a model to use,
        two teams that will be compared
        """
        self.root.title("Bl-predictor GUI")
        self.root.geometry("500x500")

        self._coming_matchday()
        self._timeframe_slider()
        self._activate_crawler()

        self.root.mainloop()

    def _coming_matchday(self):
        now = date.today()
        date_label = tk.Label(text=now)
        date_label.pack()
        current_year = now.year

        matchday_label = tk.Label(text="Upcoming Matches: ")
        matchday_label.pack()

        first_day_of_season = 1
        last_day_of_season = 34

        current_season = fetch_data([first_day_of_season, current_year], [last_day_of_season, current_year])
        matchday = current_season.head(9)
        season_label = tk.Label(text=matchday['home_team'] + " gegen " + matchday['guest_team'])
        season_label.pack()

    def _timeframe_slider(self):
        date_label = tk.Label(text="Choose a period of time:")
        date_label.pack()

        first_recorded_bl_year = 1964
        self.slider = Slider(self.root, width=400,
                             height=60,
                             min_val=first_recorded_bl_year,
                             max_val=datetime.datetime.now().year,
                             init_lis=[first_recorded_bl_year,
                                       datetime.datetime.now().year],
                             show_value=True)
        self.slider.pack()

    def _activate_crawler(self):
        download_time_label = tk.Label(text="Downloading might take a while")
        download_time_label.pack()

        self.act_crawler_button = tk.Button(
            self.root,
            text="Download Data",
            command=self._activate_crawler_helper)
        self.act_crawler_button.pack()

    def _activate_crawler_helper(self):
        first_day_of_season = 1
        last_day_of_season = 34

        self.crawler_data = fetch_data([first_day_of_season,
                                        int(self.slider.get_values()[0])],
                                       [last_day_of_season,
                                        int(self.slider.get_values()[1])])
        self.act_crawler_button.config(text='Download complete',
                                       background='green')
        # Show model selection menu
        self._choose_model()

    def _choose_model(self):
        # Create a list of all available models
        model_list = [m[0] for m in
                      inspect.getmembers(models, inspect.isclass)
                      if m[1].__module__ == models.__name__]
        # remove classes that are no models
        if "WholeDataFrequencies" in model_list:
            model_list.remove("WholeDataFrequencies")

        # Menu title shown above
        model_label = tk.Label(text="Choose a prediction model:")
        model_label.pack()
        # Initialize options
        self.model_variable = tk.StringVar(self.root)
        self.model_variable.set(model_list[0])
        model_opt = tk.OptionMenu(self.root, self.model_variable, *model_list)
        model_opt.pack()

        # Show train model button
        self._train_model()

    def _train_model(self):
        self.train_ml_button = tk.Button(
            self.root,
            text="Train prediction model",
            command=self._train_model_helper)
        self.train_ml_button.pack()

    def _train_model_helper(self):
        self.trained_model = getattr(models, self.model_variable.get())(
            self.crawler_data)
        self.train_ml_button.config(text='Model trained',
                                    background='green')

        # Show team selection menu
        self._choose_teams()

    def _choose_teams(self):
        # Create a list of all home and guest teams and drop duplicates
        try:
            option_list = self.crawler_data['home_team']
            option_list = option_list.append(self.crawler_data['guest_team'])
            option_list = sorted(option_list.drop_duplicates())
        except KeyError:
            option_list = ["Team1", "Team2"]

        # Hometeam dropdown list
        ht_label = tk.Label(self.root, text="Home team:")
        ht_label.pack()

        self.ht_variable = tk.StringVar(self.root)
        self.ht_variable.set(option_list[0])
        ht_opt = tk.OptionMenu(self.root, self.ht_variable, *option_list)
        ht_opt.pack()

        # Guestteam dropdown list
        gt_label = tk.Label(self.root, text="Guest team:")
        gt_label.pack()

        self.gt_variable = tk.StringVar(self.root)
        self.gt_variable.set(option_list[0])
        gt_opt = tk.OptionMenu(self.root, self.gt_variable, *option_list)
        gt_opt.pack()

        # Show prediction button
        self._make_prediction()

    def _make_prediction(self):
        self.prediction_button = tk.Button(
            self.root,
            text="Show predicted winner!",
            command=self._make_prediction_helper)
        self.prediction_button.pack()

    def _make_prediction_helper(self):
        self.winner = self.trained_model.predict_winner(
            self.ht_variable.get(),
            self.gt_variable.get())
        self.prediction_button.config(text='Winner predicted',
                                      background='green')

        if self.winner is None:
            # No matches in data
            self.winner = "Not enough data"

        self.prediction = tk.Label(self.root, text="Not calculated")
        self.prediction.pack()

        self.prediction.configure(text=(self.ht_variable.get() + " vs "
                                        + self.gt_variable.get()
                                        + ": "
                                        + self.winner))
