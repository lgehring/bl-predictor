"""
This module contains the GUI code.
"""

import datetime
import inspect
import tkinter as tk
from datetime import date

import pandas as pd

from bl_predictor import crawler
from bl_predictor import models
from bl_predictor.gui_slider_widget import Slider


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
        self.root.geometry("500x800")

        self._upcoming_matchday()
        self._timeframe_slider()

        self.root.mainloop()

    def _upcoming_matchday(self):
        now = date.today()
        date_label = tk.Label(text=now)
        date_label.pack()

        # signals crawler to crawl unfinished matches
        current_season = crawler.fetch_data([0, 0], [0, 0])
        for i in range(9):
            if current_season['matchday'][i] \
                    != current_season['matchday'][i + 1]:
                first_game = i + 1
                matchday = current_season.loc[i + 1:i + 9]

        upcoming_matchday = current_season['matchday'][0]

        matchday_label = \
            tk.Label(
                text="Upcoming Matchday: Matchday " + str(upcoming_matchday))
        matchday_label.pack()

        matchdaygames_label = tk.Label(text="Upcoming Matches: ")
        matchdaygames_label.pack()

        for i in range(first_game, first_game + 8):
            # shows date and time of each match
            day_label = tk.Label(text=matchday['date_time'][i])
            day_label.pack()
            # shows match
            h_t_name = matchday['home_team'][i]
            g_t_name = matchday['guest_team'][i]
            season_label = tk.Label(text=h_t_name + " vs " + g_t_name)
            season_label.pack()

    def _timeframe_slider(self):
        self.date_label = tk.Label(text="Choose a period of time:")
        self.date_label.pack()

        first_recorded_bl_year = 2003  # 1964 openliga has only new matches
        self.slider = Slider(self.root, width=400,
                             height=60,
                             min_val=first_recorded_bl_year,
                             max_val=datetime.datetime.now().year,
                             init_lis=[first_recorded_bl_year + 0.4,  # padding
                                       datetime.datetime.now().year],
                             show_value=True)
        self.slider.pack()
        self._activate_crawler()

    def _activate_crawler(self):
        self.download_time_label = tk.Label(
            text="Downloading might take a while")

        self.download_time_label.pack()

        self.act_crawler_button = tk.Button(
            self.root,
            text="Download Data",
            command=self._activate_crawler_helper)
        self.act_crawler_button.pack()

    def _activate_crawler_helper(self):
        first_day_of_season = 1
        last_day_of_season = 34

        self.crawler_data = crawler.fetch_data([first_day_of_season,
                                                int(self.slider.get_values()
                                                    [0])],
                                               [last_day_of_season,
                                                int(self.slider.get_values()
                                                    [1])])
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
        self.model_label = tk.Label(text="Choose a prediction model:")
        self.model_label.pack()
        # Initialize options
        self.model_variable = tk.StringVar(self.root)
        self.model_variable.set(model_list[0])
        self.model_opt = tk.OptionMenu(self.root, self.model_variable,
                                       *model_list)
        self.model_opt.pack()

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
        self.ht_label = tk.Label(self.root, text="Home team:")
        self.ht_label.pack()

        self.ht_variable = tk.StringVar(self.root)
        self.ht_variable.set(option_list[0])
        self.ht_opt = tk.OptionMenu(self.root, self.ht_variable, *option_list)
        self.ht_opt.pack()

        # Guestteam dropdown list
        self.gt_label = tk.Label(self.root, text="Guest team:")
        self.gt_label.pack()

        self.gt_variable = tk.StringVar(self.root)
        self.gt_variable.set(option_list[0])
        self.gt_opt = tk.OptionMenu(self.root, self.gt_variable, *option_list)
        self.gt_opt.pack()

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
        self._reset_button()

    def _reset_button(self):
        self.reset_button = tk.Button(
            self.root,
            text="Reset",
            command=self._reset_values)
        self.reset_button.pack()

    def _reset_values(self):
        self.prediction_button.pack_forget()
        self.train_ml_button.pack_forget()
        self.act_crawler_button.pack_forget()
        self.download_time_label.pack_forget()
        self.date_label.pack_forget()
        self.slider.pack_forget()
        self.prediction.pack_forget()
        self.prediction_button.pack_forget()
        self.gt_opt.pack_forget()
        self.ht_opt.pack_forget()
        self.gt_label.pack_forget()
        self.ht_label.pack_forget()
        self.model_label.pack_forget()
        self.model_opt.pack_forget()

        self.reset_button.pack_forget()

        self.crawler_data = pd.DataFrame()
        self.picked_home_team = None
        self.picked_guest_team = None
        self._timeframe_slider()
