"""
Add your GUI code here.
"""
# Importing tkinter module
from tkinter import *

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
selected_guest_team = ''
selected_home_team = ''


def fetch_crawler_data():
    crawler_data = fetch_data()  # calls for crawler data with crawler class
    return crawler_data


def train_model():
    trained_model = FrequencyModel(fetch_crawler_data)
    return trained_model


def pick_guestteam(*args):
    selected_guest_team.var_guest_team.get()


def pick_hometeam(*args):
    selected_home_team.var_home_team.get()


actCrawlerButton = Button(root, text="Activate Crawler!", command=fetch_crawler_data)
actCrawlerButton.pack()
trainMLButton = Button(root, text="Start the Algorithm!", command=train_model)
trainMLButton.pack()
winProbButton = Button(root, text="Show win probability percent!",
                       command=FrequencyModel.predict_winner(train_model(), selected_home_team, selected_guest_team))
winProbButton.pack()

# def listHomeTeam()
# drop down lists for teams
OptionList_home_team = fetch_crawler_data()['home_team']
var_home_team = StringVar(root)
var_home_team.set(OptionList_home_team[0])
opt_ht = OptionMenu(root, var_home_team, *OptionList_home_team)
opt_ht.config(width=10, font=('Helvetica', 12))
var_home_team.trace("w", pick_hometeam)
opt_ht.pack()

OptionList_guest_team = fetch_crawler_data()['home_team']
var_guest_team = StringVar(root)
var_guest_team.set(OptionList_guest_team[0])
opt_gt = OptionMenu(root, var_guest_team, *OptionList_guest_team)
opt_gt.config(width=10, font=('Helvetica', 12))
var_guest_team.trace("w", pick_guestteam)
opt_gt.pack()

root.mainloop()
# For demo purposes, this is how you could access methods from other
# modules:
data = fetch_data()  # TODO: unnecessary : remove when implemented
model = FrequencyModel()
winner = model.predict_winner('Tübingen', 'Leverkusen')
print(winner)
