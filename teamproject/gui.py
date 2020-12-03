"""
This module contains the GUI code.
"""

import tkinter as tk

from teamproject.crawler import fetch_data
from teamproject.models import FrequencyModel


def main():
    """
    Creates and shows the main GUI window.
    """
    # TODO: example, will be customizable in next issue
    start = [1, 2000]
    end = [1, 2010]

    crawler_data = fetch_data(start, end)
    trained_model = FrequencyModel(crawler_data)
    picked_guest_team = None
    picked_home_team = None
    winner = None

    # Callbacks: Called when team in dropdown menu is changed
    def pick_hometeam(*args):
        nonlocal picked_home_team
        picked_home_team = ht_variable.get()

    def pick_guestteam(*args):
        nonlocal picked_guest_team
        picked_guest_team = gt_variable.get()

    # Makes prediction based on selection and outputs it as label
    def prediction():
        nonlocal trained_model
        nonlocal picked_home_team
        nonlocal picked_guest_team
        nonlocal winner
        winner = FrequencyModel.predict_winner(trained_model, picked_home_team,
                                               picked_guest_team)
        win_prob_button.config(background='green')
        tk.Label.configure(label_pred, text=winner)
        label_pred.pack()

    # GUI window
    root = tk.Tk()  # initialize
    root.title("bl-predictor GUI")  # set window title
    root.geometry("400x400")  # set window size

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
        trained_model = FrequencyModel(crawler_data)
        train_ml_button.config(background='green')

    # Crawler button
    act_crawler_button = tk.Button(root, text="Activate Crawler!",
                                   command=fetch_crawler_data)
    act_crawler_button.pack()  # append button to GUI window

    # Train button
    train_ml_button = tk.Button(root, text="Start the Algorithm!",
                                command=train_model)
    train_ml_button.pack()  # append button to GUI window

    # Create a list of all home and guest teams and drop duplicates
    option_list = crawler_data['home_team']
    option_list = option_list.append(crawler_data['guest_team'])
    option_list = option_list.drop_duplicates()

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
                                           text="Show win probability percent!",
                                           command=prediction)
    win_prob_button.pack()  # append button to GUI window

    # Label with predicted winner
    label_winner = tk.Label(root, text="Predicted winner:")
    label_winner.pack()  # append label to GUI window

    # Prediction label
    label_pred = tk.Label(root, text="None")
    label_pred.pack()  # append label to GUI window

    root.mainloop()
