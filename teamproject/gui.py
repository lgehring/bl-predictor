"""
Add your GUI code here.
"""
# Importing tkinter module
from tkinter import *
import pandas as pd

import data as data

from teamproject.crawler import fetch_data
from teamproject.models import FrequencyModel


def main():
    """
    Creates and shows the main window.
    """
    # Add code here to create and initialize window.


# creating Tk window
root = Tk()
root.title("Football League Matches Predictor")
root.geometry("400x400")


def fetch_crawler_data():
    crawler_data = fetch_data()  # calls for crawler data with crawler class
    return crawler_data


def train_model():
    trained_model = FrequencyModel(fetch_crawler_data)
    return trained_model


def pick_guestteam(list, *args):
    picked_guest_team = var_home_team.get()


def pick_hometeam(list, *args):
    picked_home_team = var_home_team.get()


actCrawlerButton = Button(root, text="Activate Crawler!", command=fetch_crawler_data)
actCrawlerButton.pack()
trainMLButton = Button(root, text="Start the Algorithm!", command=train_model)
trainMLButton.pack()
trained_model = train_model()

# winProbButton = Button(root, text="Show win probability percent!",
#                      command=trained_model.predict_winner(picked_teams[0], picked_teams[1]))
# winProbButton.pack()


# drop down lists for teams
# make option list
OptionList = fetch_crawler_data()['home_team']
#append list of hometeams with list of guestteam
OptionList = OptionList.append(fetch_crawler_data()['guest_team'])
OptionList = OptionList.drop_duplicates()

#make hometeam dropdown
var_home_team = StringVar(root)
var_home_team.set(OptionList[0])
opt_ht = OptionMenu(root, var_home_team, *OptionList)
opt_ht.config(width=10, font=('Helvetica', 12))
var_home_team.trace("w", pick_hometeam)
opt_ht.pack()

#make guestteam dropdown
var_guest_team = StringVar(root)
var_guest_team.set(OptionList[0])
opt_gt = OptionMenu(root, var_guest_team, *OptionList)
opt_gt.config(width=10, font=('Helvetica', 12))
var_guest_team.trace("w", pick_guestteam)
opt_gt.pack()

root.mainloop()
