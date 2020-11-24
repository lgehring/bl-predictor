"""
This module contains the GUI code.
"""

from tkinter import *
from tkinter import Button

import pandas as pd

from teamproject.crawler import fetch_data
from teamproject.models import FrequencyModel

# global variabels
crawler_data = pd.DataFrame()
trained_model = FrequencyModel(None)
picked_guest_team = ""
picked_home_team = ""
winner = ""


def fetch_crawler_data():
    global crawler_data
    crawler_data = fetch_data()


def train_model():
    global crawler_data
    global trained_model
    trained_model = FrequencyModel(crawler_data)


def prediction():
    global trained_model
    global picked_home_team
    global picked_guest_team
    global winner
    winner = FrequencyModel.predict_winner(trained_model, picked_home_team, picked_guest_team)
    print(winner)


def main():
    global winner
    """
Creates and shows the main window.
    """
    # creating Tk window
    root = Tk()
    root.title("Football League Matches Predictor")
    root.geometry("400x400")
    # creating first two buttons
    act_crawler_button = Button(root, text="Activate Crawler!", command=fetch_crawler_data)
    act_crawler_button.pack()
    train_ml_button = Button(root, text="Start the Algorithm!", command=train_model)
    train_ml_button.pack()

    # drop down lists for teams
    # make option list
    option_list = fetch_data()['home_team']
    # append list of hometeams with list of guestteam
    option_list = option_list.append(fetch_data()['guest_team'])
    option_list = option_list.drop_duplicates()

    # methods to choose a team
    def pick_hometeam(*args):
        global picked_home_team
        picked_home_team = var_home_team.get()

    def pick_guestteam(*args):
        global picked_guest_team
        picked_guest_team = var_guest_team.get()
        if picked_home_team == picked_home_team:
            raise Exception("Sorry, you need to choose a different home- or guestteam")

    # make hometeam dropdown
    var_home_team = StringVar(root)
    var_home_team.set(option_list[0])
    opt_ht = OptionMenu(root, var_home_team, *option_list)
    opt_ht.config(width=10, font=('Helvetica', 12))
    label_ht = Label(root, text="Home-team: ", font="Arial 12", anchor='w')
    label_ht.pack(side="top", fill="y")
    var_home_team.trace("w", pick_hometeam)
    opt_ht.pack()

    # make guestteam dropdown
    var_guest_team = StringVar(root)
    var_guest_team.set(option_list[0])
    opt_gt = OptionMenu(root, var_guest_team, *option_list)
    opt_gt.config(width=10, font=('Helvetica', 12))
    label_ht = Label(root, text="Guest-team: ", font="Arial 12", anchor='w')
    label_ht.pack(side="top", fill="y")
    var_guest_team.trace("w", pick_guestteam)
    opt_gt.pack()

    # button to predict winner
    win_prob_button: Button = Button(root, text="Show win probability percent!",
                                     command=prediction)
    win_prob_button.pack()

    # label with predicted winner
    label_winner = Label(root, text="the predicted winner is: ", font="Arial 12", anchor='w')
    label_winner.pack(side="top", fill="y")

    root.mainloop()


main()
