"""
This module contains the GUI code.
"""

import inspect
import tkinter as tk
import datetime

from teamproject import models
from teamproject.crawler import fetch_data


def main():
    """
    Creates and shows the main GUI window.
    """
    # TODO: example, will be customizable in next issue
    start = [20, 2019]
    end = [1, datetime.datetime.now().year]

    crawler_data = fetch_data(start, end)
    trained_model = None
    picked_guest_team = None
    picked_home_team = None
    winner = None

    # Callbacks: Called when team in dropdown menu is changed
    # noinspection PyUnusedLocal
    def pick_hometeam(*args):
        nonlocal picked_home_team
        picked_home_team = ht_variable.get()

    # noinspection PyUnusedLocal
    def pick_guestteam(*args):
        nonlocal picked_guest_team
        picked_guest_team = gt_variable.get()

    # Makes prediction based on selection and outputs it as label
    def prediction():
        nonlocal trained_model
        nonlocal picked_home_team
        nonlocal picked_guest_team
        nonlocal winner
        # disables warning for unknown reference before training model
        # noinspection PyUnresolvedReferences
        winner = trained_model.predict_winner(picked_home_team,
                                              picked_guest_team)
        win_prob_button.config(background='green')
        tk.Label.configure(label_pred, text=winner)
        label_pred.pack()

    # GUI window
    root = tk.Tk()  # initialize
    root.title("teamproject GUI")  # set window title
    root.geometry("500x500")  # set window size

    # Methods activated on button press
    def fetch_crawler_data():
        nonlocal crawler_data
        # TODO: prevent double crawler instance from running
        # data is automatically scraped at gui launch
        # crawler_data = fetch_data(start, end)
        act_crawler_button.config(background='green')

    def train_model():
        nonlocal crawler_data
        nonlocal trained_model
        trained_model = getattr(models, model_variable.get())(crawler_data)
        train_ml_button.config(background='green')

    def pick_day1(*args):
        nonlocal start
        start[0] = days1_variable.get()

    def pick_season1(*args):
        nonlocal start
        start[1] = seasons1_variable.get()

    def pick_day2(*args):
        nonlocal end
        end[0] = days2_variable.get()

    def pick_season2(*args):
        nonlocal end
        end[1] = seasons1_variable.get()

    # TODO: data-selection slider
    date_label = tk.Label(text="chose a period of time:")
    date_label.pack()
    date_label = tk.Label(text="from:")
    date_label.pack()
    # frame for first date
    firstd_frame = tk.Frame(root)
    firstd_frame.pack()

    date_label = tk.Label(text="until:")
    date_label.pack()
    # frame for second date
    secondd_frame = tk.Frame(root)
    secondd_frame.pack()

    # data-selection drop downs
    option_list_days = list(range(1, 35))
    option_list_seasons = list(range(1964, datetime.datetime.now().year))

    # 2 drop down lists for first date
    # drop down list for the day
    days1_variable = tk.StringVar(root)
    days1_variable.set(option_list_days[0])
    days1_opt = tk.OptionMenu(firstd_frame, days1_variable, *option_list_days)
    days1_opt.pack(side=tk.LEFT)
    # drop down list for the season
    seasons1_variable = tk.StringVar(root)
    seasons1_variable.set(option_list_seasons[0])
    seasons1_opt = tk.OptionMenu(firstd_frame, seasons1_variable,
                                 *option_list_seasons)
    seasons1_opt.pack(side=tk.LEFT)

    # nother 2 drop down lists for second date
    # 2 drop down lists for first date
    # drop down list for the day
    days2_variable = tk.StringVar(root)
    days2_variable.set(option_list_days[0])
    days2_opt = tk.OptionMenu(secondd_frame, days2_variable, *option_list_days)
    days2_opt.pack(side=tk.LEFT)
    # drop down list for the season
    seasons2_variable = tk.StringVar(root)
    seasons2_variable.set(option_list_seasons[0])
    seasons2_opt = tk.OptionMenu(secondd_frame, seasons2_variable,
                                 *option_list_seasons)
    seasons2_opt.pack(side=tk.RIGHT)

    days1_variable.trace("w", pick_day1)
    seasons1_variable.trace("w", pick_season1)
    days2_variable.trace("w", pick_day2)
    seasons2_variable.trace("w", pick_season2)

    # Crawler button
    act_crawler_button = tk.Button(root, text="Activate Crawler!",
                                   command=fetch_crawler_data)
    act_crawler_button.pack()  # append button to GUI window

    # Create a list of all available models
    model_list = [m[0] for m in inspect.getmembers(models, inspect.isclass)
                  if m[1].__module__ == models.__name__]

    # Models dropdown list
    # Menu title shown above
    model_label = tk.Label(text="Prediction model:")
    model_label.pack()
    # Initialize options
    model_variable = tk.StringVar(root)
    model_variable.set(model_list[0])
    model_opt = tk.OptionMenu(root, model_variable, *model_list)
    model_opt.pack()

    # Train button
    train_ml_button = tk.Button(root, text="Start the Algorithm!",
                                command=train_model)
    train_ml_button.pack()  # append button to GUI window

    # Create a list of all home and guest teams and drop duplicates
    option_list = crawler_data['home_team']
    option_list = option_list.append(crawler_data['guest_team'])
    option_list = sorted(option_list.drop_duplicates())

    # Hometeam dropdown list
    # Menu title shown above
    ht_label = tk.Label(text="Home team:")
    ht_label.pack()
    # Initialize options
    ht_variable = tk.StringVar(root)
    ht_variable.set(option_list[0])
    ht_opt = tk.OptionMenu(root, ht_variable, *option_list)
    ht_opt.pack()
    # "Listens" for selection and calls callback method
    ht_variable.trace("w", pick_hometeam)

    # Guestteam dropdown list
    # Menu title shown above
    gt_label = tk.Label(text="Guest team:")
    gt_label.pack()

    # Initialize options
    gt_variable = tk.StringVar(root)
    gt_variable.set(option_list[0])
    gt_opt = tk.OptionMenu(root, gt_variable, *option_list)
    gt_opt.pack()
    # "Listens" for selection and calls callback method
    gt_variable.trace("w", pick_guestteam)

    # Prediction button
    win_prob_button: tk.Button = tk.Button(root,
                                           text="Show predicted winner!",
                                           command=prediction)
    win_prob_button.pack()  # append button to GUI window

    # Label with predicted winner
    label_winner = tk.Label(root, text="Predicted winner:")
    label_winner.pack()  # append label to GUI window

    # Prediction label
    label_pred = tk.Label(root, text="None")
    label_pred.pack()  # append label to GUI window

    root.mainloop()
