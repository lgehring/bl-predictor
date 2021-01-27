"""
This module contains the GUI code.
"""

import datetime
import inspect
import os
import tkinter as tk
from datetime import date

import pandas as pd
from PIL import ImageTk, Image

from bl_predictor import crawler
from bl_predictor import models
from bl_predictor.gui_slider_widget import Slider


class MainWindow:
    """
    Graphical User Interface for the bl_predictor project.

    The GUI window can be shown with show_window()
    """

    def __init__(self):
        """
        Init MainClass.

        Initializes interpreter and creates root window.
        Stores crawled data.
        Stores the home- and guest-team.

        :type self:
        """
        self.root = tk.Tk()

        self.crawler_data = pd.DataFrame()
        self.picked_home_team = None
        self.picked_guest_team = None

    def show_window(self):
        """
        Shows the bl_predictor GUI.
        The function constructs a window with matches of the upcoming matchday,
        a timeframe slider and activates the crawler.
        """
        self.root.title("Bl-predictor GUI")
        self.root.geometry("800x800")

        self._upcoming_matchday()
        self._timeframe_slider()
        self._activate_crawler()

        self.root.mainloop()

    def _upcoming_matchday(self):
        """
        Writes matches of upcoming matchday in the window. This includes
        date and time of the matches, the teams that are going to
        play and their logos.
        """
        now = date.today()
        date_label = tk.Label(text=now)
        date_label.grid(sticky=tk.W)

        # signals crawler to crawl unfinished matches
        current_season = crawler.fetch_data([0, 0], [0, 0])
        num_games_a_day = 9

        # checking if first 9 games of current season are on the same day
        for i in range(num_games_a_day):
            if current_season['matchday'][i] \
                    != current_season['matchday'][i + 1]:
                first_game = i + 1
                matchday = current_season.loc[i + 1:i + 9]

        upcoming_matchday = current_season['matchday'][0]

        matchday_label = \
            tk.Label(
                text="Upcoming Matchday: Matchday " + str(upcoming_matchday),
                font=("Calibri Light", 30))
        matchday_label.grid(columnspan=5)

        matchdaygames_label = tk.Label(text="Upcoming Matches: ",
                                       font=("Calibri Light", 25))
        matchdaygames_label.grid(columnspan=5)

        # path of gui.py
        gui_path = os.path.abspath(__file__)
        # path to team project
        dir_path = os.path.dirname(gui_path)
        last_game = first_game + 9
        for i in range(first_game, last_game):
            # loads the logos into gui
            self.image1 = Image.open(
                dir_path + "/team_logos/" + matchday['home_team'][i] + ".png")
            self.image2 = Image.open(
                dir_path + "/team_logos/" + matchday['guest_team'][i] + ".png")
            self.image1 = self.image1.resize((30, 30), Image.ANTIALIAS)
            self.image2 = self.image2.resize((30, 30), Image.ANTIALIAS)
            self.img1 = ImageTk.PhotoImage(self.image1)
            self.img2 = ImageTk.PhotoImage(self.image2)
            self.panel1 = tk.Label(self.root, image=self.img1)
            self.panel2 = tk.Label(self.root, image=self.img2)
            self.panel1.photo = self.img1
            self.panel2.photo = self.img2

            # shows date and time of each match
            if i == first_game or \
                    matchday['date_time'][i] != matchday['date_time'][i - 1]:
                day_label = tk.Label(text=matchday['date_time'][i],
                                     font=("Calibri Light", 13))
                day_label.grid(columnspan=5)
            # shows match
            home_label = tk.Label(text=matchday['home_team'][i],
                                  font=("Calibri Light", 13))
            versus_label = tk.Label(text=" vs ",
                                    font=("Calibri Light", 13))
            guest_label = tk.Label(text=matchday['guest_team'][i],
                                   font=("Calibri Light", 13))

            home_label.grid(row=2 * i, column=0, sticky=tk.E)
            self.panel1.grid(row=2 * i, column=1)
            versus_label.grid(row=2 * i, column=2, padx=10)
            self.panel2.grid(row=2 * i, column=3)
            guest_label.grid(row=2 * i, column=4, sticky=tk.W)

            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_columnconfigure(4, weight=1)

    def _timeframe_slider(self):
        """
        Builds a slider ro adjust the to crawl period.
        """
        date_label = tk.Label(text="Choose a period of time:",
                              font=("Calibri Light", 13))
        date_label.grid(columnspan=5)

        first_recorded_bl_year = 2003  # 1964, Openliga has only new matches
        self.slider = Slider(self.root, width=400,
                             height=60,
                             min_val=first_recorded_bl_year,
                             max_val=datetime.datetime.now().year,
                             init_lis=[first_recorded_bl_year + 0.4,  # padding
                                       datetime.datetime.now().year],
                             show_value=True)
        self.slider.grid(columnspan=5)

    def _activate_crawler(self):
        """
        Builds Download button. When used _activate_crawler_helper is
        activated, to crawl the data in selected time range.
        """
        download_time_label = tk.Label(text="Downloading might take a while",
                                       font=("Calibri Light", 13))
        download_time_label.grid(columnspan=5)

        self.act_crawler_button = tk.Button(
            self.root,
            text="Download Data",
            font=("Calibri Light", 13),
            command=self._activate_crawler_helper)
        self.act_crawler_button.grid(columnspan=5)

    def _activate_crawler_helper(self):
        """
        Takes values from slider and fetches the data between these seasons
        Begins on 1. matchday of first value until last matchday of the second
        value.
        After completion the button signal this and _choose_model is activated,
        which shows the model selection menu.
        """
        first_day_of_season = 1
        last_day_of_season = 34

        self.crawler_data = crawler.fetch_data(
            [first_day_of_season, int(self.slider.get_values()[0])],
            [last_day_of_season, int(self.slider.get_values()[1])])
        self.act_crawler_button.config(text='Download complete',
                                       background='green')
        # Show model selection menu
        self._choose_model()

    def _choose_model(self):
        """
        Builds list of training models to choose from.
        """
        # Create a list of all available models
        model_list = [m[0] for m in
                      inspect.getmembers(models, inspect.isclass)
                      if m[1].__module__ == models.__name__]

        # Menu title shown above
        model_label = tk.Label(text="Choose a prediction model:")
        model_label.grid(columnspan=5)
        # Initialize options
        self.model_variable = tk.StringVar(self.root)
        self.model_variable.set(model_list[0])
        model_opt = tk.OptionMenu(self.root, self.model_variable, *model_list)
        model_opt.grid(columnspan=5)

        # Show train model button
        self._train_model()

    def _train_model(self):
        """
        Builds button to train the model. It activates _train_model_helper.
        """
        self.train_ml_button = tk.Button(
            self.root,
            text="Train prediction model",
            command=self._train_model_helper)
        self.train_ml_button.grid(columnspan=5)

    def _train_model_helper(self):
        """
        Trains Model. When completed title and color of the button signals it
        is finished.
        """
        self.trained_model = getattr(models, self.model_variable.get())(
            self.crawler_data)
        self.train_ml_button.config(text='Model trained',
                                    background='green')

        # Show team selection menu
        self._choose_teams()

    def _choose_teams(self):
        """
        Creates a list of all home and guest teams and drops duplicates.
        When completed the function activates _make_prediction, it shows a
        prediction button
        """
        try:
            option_list = self.crawler_data['home_team']
            option_list = option_list.append(self.crawler_data['guest_team'])
            option_list = sorted(option_list.drop_duplicates())
        except KeyError:
            option_list = ["Team1", "Team2"]

        # home team dropdown list
        ht_label = tk.Label(self.root, text="Home team:")
        ht_label.grid(columnspan=5)

        self.ht_variable = tk.StringVar(self.root)
        self.ht_variable.set(option_list[0])
        ht_opt = tk.OptionMenu(self.root, self.ht_variable, *option_list)
        ht_opt.grid(columnspan=5)

        # guest team dropdown list
        gt_label = tk.Label(self.root, text="Guest team:")
        gt_label.grid(columnspan=5)

        self.gt_variable = tk.StringVar(self.root)
        self.gt_variable.set(option_list[0])
        gt_opt = tk.OptionMenu(self.root, self.gt_variable, *option_list)
        gt_opt.grid(columnspan=5)

        # Show prediction button
        self._make_prediction()

    def _make_prediction(self):
        """
        Button to activate prediction of the winner.
        """
        self.prediction_button = tk.Button(
            self.root,
            text="Show predicted winner!",
            command=self._make_prediction_helper)
        self.prediction_button.grid(columnspan=5)

    def _make_prediction_helper(self):
        """
        Predicts the winner of the two selected teams. Button signals when
        it's finished. A label will let you know if there is not enough data
        for the prediction.
        """
        self.winner = self.trained_model.predict_winner(
            self.ht_variable.get(),
            self.gt_variable.get())
        self.prediction_button.config(text='Winner predicted',
                                      background='green')

        if self.winner is None:
            # No matches in data
            self.winner = "Not enough data"

        self.prediction = tk.Label(self.root, text="Not calculated")
        self.prediction.grid(columnspan=5)

        self.prediction.configure(text=(self.ht_variable.get() + " vs "
                                        + self.gt_variable.get()
                                        + ": "
                                        + self.winner))