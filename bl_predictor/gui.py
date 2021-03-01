"""
This module contains the GUI code.
"""

import inspect
import os
import tkinter as tk
import tkinter.ttk as ttk
from datetime import date

import pandas as pd
from PIL import ImageTk, Image
from ttkthemes import ThemedStyle

from bl_predictor import crawler
from bl_predictor import models
from bl_predictor.gui_slider_widget import Slider


class MainWindow:
    """
    Graphical User Interface for the bl_predictor project.

    The GUI window can be shown with show_window()
    """

    def __init__(self, test):
        """
        Init MainClass.

        Initializes interpreter and creates root window.
        Stores crawled data.
        Stores the home- and guest-team.


        :param str test: str or none. Put in "test" for an object to be
            tested. None otherwise. For a test object there is no
            implementation of a mainloop.

        :type self:
        """
        self.test = test
        self.root = tk.Tk()
        # initialize Frame for results
        self.right = ttk.Frame(self.root)

        self.crawler_data = pd.DataFrame()
        self.picked_home_team = None
        self.picked_guest_team = None
        # This boolean variable keeps track of the current main window theme
        self.default_theme = True
        self.current_season = crawler.get_current_date()[1]

        # path of gui.py
        self.gui_path = os.path.abspath(__file__)
        # path to team project
        self.dir_path = os.path.dirname(self.gui_path)

        self.style = ThemedStyle(self.root)

        self.show_window()

    def show_window(self):
        """
        Shows the bl-predictor GUI.

        Options to choose
        a timeframe for data-crawling,
        a model to use,
        two teams that will be compared
        """
        self.root.title("Bl-predictor GUI")
        self.root.geometry("1400x750")
        self.root.state('zoomed')
        self.root.attributes("-fullscreen", True)

        self.root.grid_rowconfigure(21, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        self.right.grid(row=3, column=5, padx=2, pady=5, rowspan=40,
                        sticky="N")

        result_label = ttk.Label(self.root,
                                 text="Results",
                                 font=("Calibri Light", 25, 'bold'))
        result_label.grid(row=2, column=5, padx=180, pady=10,
                          sticky=tk.S)
        # Sets the theme
        self.style.set_theme("arc")
        self.root.config(bg="#f5f6f7")

        # Adding space to edge
        upper_space = ttk.Label(self.root,
                                text="",
                                font=20)
        upper_space.grid(row=1, pady=10, columnspan=7)

        right_empty_column = ttk.Label(self.root,
                                       text="",
                                       font=20)
        right_empty_column.grid(column=6, row=0, padx=20, columnspan=7)

        self._menu_bar()
        self._upcoming_matchday()
        self._blpredictor_logo()
        self._timeframe_slider()

        # if an object is made for testing it does not have a mainloop
        if self.test != "test":
            self.root.mainloop()

    def _menu_bar(self):
        """
        Adds a menu bar for the main window, with "Exit"
        and "Switch Theme" buttons
        """
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        switch_theme_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Options", menu=switch_theme_menu)
        switch_theme_menu.add_command(
            label="Switch Theme", command=self.switch_theme)
        switch_theme_menu.add_command(label="Exit", command=self.root.destroy)

    def switch_theme(self):
        """
        Builds menu bar button functionality to switch between Themes
        """
        if self.default_theme:
            self.default_theme = False
            self.night_on()
        else:
            self.default_theme = True
            self.night_off()

    def night_on(self):
        """
        Activates Night Theme for whole window
        """
        self.style.set_theme("equilux")
        # equilux's background color is dark grey
        self.root.config(bg="#464646")
        self.slider.canv.configure(bg="#464646")
        self.slider.canv.itemconfig(self.slider.id_value, fill="#a6a6a6")
        self.my_canvas_final.config(bg='#464646')

    def night_off(self):
        """
        Goes back to to Default Theme for whole window
        """
        self.style.set_theme("arc")
        # arc's background color is almost white
        self.root.config(bg="#f5f6f7")
        self.slider.canv.configure(bg="#f5f6f7")
        self.slider.canv.itemconfig(self.slider.id_value, fill="#5c616c")
        self.my_canvas_final.config(bg='#f5f6f7')

    def _upcoming_matchday(self):
        """
        Writes matches of upcoming matchday in the window. This includes
        date and time of the matches, the teams that are going to
        play and their logos.
        """
        now = date.today().strftime("%a %d.%m.%y")
        self.date_label = ttk.Label(text=now, font="Calibri 12")
        self.date_label.grid(row=0, columnspan=2, padx=3, sticky=tk.NW)

        # signals crawler to crawl unfinished matches
        unfinished_matches = crawler.fetch_data([0, 0], [0, 0])
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        first_game = 0
        matchday = unfinished_matches.loc[first_game:first_game + 9]

        upcoming_matchday = unfinished_matches['matchday'][0]
        padding = 3

        matchday_label = \
            ttk.Label(
                text="Upcoming: " + "Matchday " + str(upcoming_matchday)
                     + ", " + str(self.current_season),
                font=("Calibri Light", 25, 'bold'))

        matchday_label.grid(pady=padding, padx=15, row=2, column=1,
                            columnspan=3)

        last_game = first_game + 9
        rowcount = 0
        for i in range(first_game, last_game):
            # loads the logos into gui
            # self.image1 = Image.open(
            #    self.dir_path + "/team_logos/" + matchday['home_team'][i]
            #                                               + ".png")
            # self.image2 = Image.open(
            #    self.dir_path + "/team_logos/" + matchday['guest_team'][i]
            #    + ".png")
            # self.image1 = self.image1.resize((30, 30), Image.ANTIALIAS)
            # self.image2 = self.image2.resize((30, 30), Image.ANTIALIAS)
            # self.img1 = ImageTk.PhotoImage(self.image1)
            # self.img2 = ImageTk.PhotoImage(self.image2)
            # self.panel1 = tk.Label(self.root, image=self.img1)
            # self.panel2 = tk.Label(self.root, image=self.img2)
            # self.panel1.photo = self.img1
            # self.panel2.photo = self.img2

            # shows date and time of each match
            if i == first_game or \
                    matchday['date_time'][i] != matchday['date_time'][i - 1]:
                day_label = ttk.Label(
                    text=matchday['date_time'][i].strftime("%a %d.%m. %H:%M"),
                    font=("Calibri Light", 17, 'bold'))
                day_label.grid(pady=padding, row=3 + rowcount,
                               column=1, columnspan=3)
                rowcount += 1
            # shows match
            home_label = ttk.Label(text=matchday['home_team'][i],
                                   font=("Calibri", 17))
            versus_label = ttk.Label(text="| vs |",
                                     font=("Calibri", 17))
            guest_label = ttk.Label(text=matchday['guest_team'][i],
                                    font=("Calibri", 17))

            home_label.grid(pady=padding, row=3 + rowcount,
                            column=1, sticky=tk.E)
            # self.panel1.grid(row=2 * i, column=1)
            versus_label.grid(pady=padding, row=3 + rowcount, column=2)
            # self.panel2.grid(row=2 * i, column=3)
            guest_label.grid(pady=padding, row=3 + rowcount,
                             column=3, sticky=tk.W)
            rowcount += 1

            self.root.grid_columnconfigure(0, weight=0)
            self.root.grid_columnconfigure(4, weight=1)

    def _blpredictor_logo(self):
        """
        Adds the application logo and packs it in the bottom right of the
        window
        """
        # Create a canvas
        self.my_canvas_final = tk.Canvas(self.root,
                                         width=100,
                                         height=100,
                                         highlightthickness=0, bg='#f5f6f7')

        self.my_canvas_final.grid(column=0, row=21, columnspan=1,
                                  sticky='SW')

        # Import the logo image and put it in the canvas
        logo_path = Image.open(os.path.join(self.dir_path,
                                            "bl-predictor_logo.png"))
        logo_resized = logo_path.resize((100, 100), Image.ANTIALIAS)
        self.logo_final = ImageTk.PhotoImage(logo_resized)
        self.my_canvas_final.create_image(0, 0, image=self.logo_final,
                                          anchor="nw")

    def _timeframe_slider(self):
        """
        Builds a slider ro adjust the to crawl period.
        """
        headline = ttk.Label(text="Prediction configuration",
                             font=("Calibri Light", 25, 'bold'))
        headline.grid(row=2, column=4)
        period_label = ttk.Label(text="Training set timespan:",
                                 font=("Calibri Light", 13))
        period_label.grid(row=3, column=4)

        first_recorded_bl_year = 2003  # 1964, Openliga has only new matches
        self.slider = Slider(self.root, width=300,
                             height=60,
                             min_val=first_recorded_bl_year,
                             max_val=self.current_season,
                             init_lis=[first_recorded_bl_year + 0.4,  # padding
                                       self.current_season],
                             show_value=True)
        self.slider.grid(row=4, column=4)

        if self.default_theme:
            self.slider.canv.configure(bg="#f5f6f7")
        else:
            self.slider.canv.configure(bg="#464646")

        self._activate_crawler()

    def _activate_crawler(self):
        """
        Builds Download button. When used _activate_crawler_helper is
        activated, to crawl the data in selected time range.
        """
        self.download_time_label = ttk.Label(
            text="Downloading might take a while",
            font=("Calibri Light", 13))
        self.download_time_label.grid(row=5, column=4)

        self.act_crawler_button = ttk.Button(
            self.root,
            text="Download Data",
            command=self._activate_crawler_helper)
        self.act_crawler_button.grid(row=6, column=4)

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

        slider_first_value = self.slider.get_values()[0]
        slider_last_value = self.slider.get_values()[1]

        self.crawler_data = crawler.fetch_data([first_day_of_season,
                                                int(slider_first_value)],
                                               [last_day_of_season,
                                                int(slider_last_value)])
        self.act_crawler_button.config(text='Download complete')
        self.act_crawler_button.config(state=tk.DISABLED)

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
        # remove classes that are no models
        if "WholeDataFrequencies" in model_list:
            model_list.remove("WholeDataFrequencies")

        # Menu title shown above
        self.model_label = ttk.Label(text="Choose a prediction model:")
        self.model_label.grid(row=7, column=4)
        # Initialize options
        self.model_variable = tk.StringVar(self.root)
        self.model_variable.set(model_list[0])
        self.model_opt = ttk.OptionMenu(self.root, self.model_variable,
                                        model_list[0],
                                        *model_list)
        self.model_opt.grid(row=8, column=4)
        # Show train model button
        self._train_model()

    def _train_model(self):
        """
        Builds button to train the model. It activates _train_model_helper.
        """
        self.train_ml_button = ttk.Button(
            self.root,
            text="Train prediction model",
            command=self._train_model_helper)
        self.train_ml_button.grid(row=9, column=4)

    def _train_model_helper(self):
        """
        Trains Model. When completed title and color of the button signals it
        is finished.
        """
        self.trained_model = getattr(models, self.model_variable.get())(
            self.crawler_data)
        self.train_ml_button.config(text='Model trained')
        self.train_ml_button.config(state=tk.DISABLED)

        result_model_label = ttk.Label(
            self.right, text=("\n"
                              + self.model_variable.get() + ", "
                              + str(int(self.slider.get_values()[0])) + " to "
                              + str(int(self.slider.get_values()[1])) + ":"))
        result_model_label.configure(font="Verdana 13 bold")
        result_model_label.pack(in_=self.right)
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
        self.ht_label = ttk.Label(self.root, text="Home team:")
        self.ht_label.grid(row=10, column=4)

        self.picked_home_team = tk.StringVar(self.root)
        self.picked_home_team.set(option_list[0])
        self.ht_opt = ttk.OptionMenu(self.root, self.picked_home_team,
                                     option_list[0],
                                     *option_list)
        self.ht_opt.grid(row=11, column=4)

        # guest team dropdown list
        self.gt_label = ttk.Label(self.root, text="Guest team:")
        self.gt_label.grid(row=12, column=4)

        self.picked_guest_team = tk.StringVar(self.root)
        self.picked_guest_team.set(option_list[0])
        self.gt_opt = ttk.OptionMenu(self.root, self.picked_guest_team,
                                     option_list[0],
                                     *option_list)
        self.gt_opt.grid(row=13, column=4)

        # Show prediction button
        self._make_prediction()

    def _make_prediction(self):
        """
        Button to activate prediction of the winner.
        """
        self.prediction_button = ttk.Button(
            self.root,
            text="Show predicted winner!",
            command=self._make_prediction_helper)
        self.prediction_button.grid(row=14, column=4)

    def _make_prediction_helper(self):
        """
        Predicts the winner of the two selected teams. Button signals when
        it's finished. A label will let you know if there is not enough data
        for the prediction.
        """
        winner = self.trained_model.predict_winner(
            self.picked_home_team.get(),
            self.picked_guest_team.get())
        self.prediction_button.config(text='Winner predicted')

        # delete first result, if necessary
        result_frame_y = self.right.winfo_height()
        height_window = 330
        results = self.right.winfo_children()
        if result_frame_y >= height_window:
            if "Model" in results[3].cget("text"):
                results[2].destroy()
                results[0].destroy()
                results[1].destroy()
            else:
                results[1].destroy()
                results[2].destroy()

        if winner is None:
            # No matches in data
            winner = "Not enough data"

        self.prediction = ttk.Label(self.right, font="Verdana 13")
        self.prediction.configure(text="\n"
                                       + (self.picked_home_team.get() + " vs "
                                          + self.picked_guest_team.get()
                                          + ": "
                                          ))

        self.prediction_percent = ttk.Label(self.right, text=winner,
                                            font="Verdana 13 bold ")

        self.prediction.pack(in_=self.right)
        self.prediction_percent.pack(in_=self.right)

        self._reset_teams_button()
        self._reset_button()
        self._reset_model_button()

        self.prediction_button.config(state=tk.DISABLED)

    def _reset_teams_button(self):
        self.reset_teams_button = ttk.Button(
            self.root,
            text="put in new teams",
            command=self._reset_teams)
        self.reset_teams_button.grid(row=17, column=5)

    def _reset_teams(self):
        self.prediction_button.grid_forget()

        self.reset_model_button.grid_forget()
        self.reset_teams_button.grid_forget()
        self.reset_button.grid_forget()
        self.ht_label.grid_forget()
        self.ht_opt.grid_forget()
        self.gt_label.grid_forget()
        self.gt_opt.grid_forget()

        self.picked_home_team = None
        self.picked_guest_team = None

        self._choose_teams()

    def _reset_model_button(self):
        self.reset_model_button = ttk.Button(
            self.root,
            text="choose new model",
            command=self._reset_model)
        self.reset_model_button.grid(row=18, column=5)

    def _reset_model(self):
        self.train_ml_button.grid_forget()
        self.model_opt.grid_forget()
        self.model_label.grid_forget()

        self.gt_label.grid_forget()
        self.ht_label.grid_forget()
        self.gt_opt.grid_forget()
        self.ht_opt.grid_forget()
        self.prediction_button.grid_forget()

        self.reset_button.grid_forget()
        self.reset_model_button.grid_forget()
        self.reset_teams_button.grid_forget()

        self.picked_home_team = None
        self.picked_guest_team = None
        self.trained_model = None

        self._choose_model()

    def _reset_button(self):
        self.reset_button = ttk.Button(
            self.root,
            text="Reset",
            command=self._reset_values)
        self.reset_button.grid(row=19, column=5)

    def _reset_values(self):
        self.slider.grid_forget()
        self.act_crawler_button.grid_forget()

        self.train_ml_button.grid_forget()

        self.gt_label.grid_forget()
        self.ht_label.grid_forget()
        self.gt_opt.grid_forget()
        self.ht_opt.grid_forget()
        self.prediction_button.grid_forget()

        self.model_label.grid_forget()
        self.model_opt.grid_forget()

        self.download_time_label.grid_forget()

        self.reset_teams_button.grid_forget()
        self.reset_button.grid_forget()
        self.reset_model_button.grid_forget()

        self.crawler_data = pd.DataFrame()
        self.picked_home_team = None
        self.picked_guest_team = None
        self._timeframe_slider()
