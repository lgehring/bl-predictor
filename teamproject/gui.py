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
'''
mainMenu = Menu(root)
root.config(menu=mainMenu)

homeTeamMenu = Menu(mainMenu)
mainMenu.add_cascade(label="Home Team", menu=homeTeamMenu)
#subMenu.add.command...


awayTeamMenu = Menu(mainMenu)
mainMenu.add_cascade(label="Away Team", menu=awayTeamMenu)

'''


# create a database or connect to one
# conn =sqlite3.connect(data)

# create cursor
# c = conn.cursor()

# create table
# c.exe

def crawlerClick():
    crawlerData = Label(root, data)
    crawlerData.pack()
    crawler_data = fetch_data()  # calls for crawler data with crawler class
    print(crawler_data)


actCrawlerButton = Button(root, text="Activate Crawler!", command=crawlerClick)
actCrawlerButton.pack()
trainMLButton = Button(root, text="Start the Algorithm!")
trainMLButton.pack()
winProbButton = Button(root, text="Show win probability percent!")
winProbButton.pack()

# drop down lists for teams

# def listHomeTeam()


root.mainloop()
# For demo purposes, this is how you could access methods from other
# modules:
data = fetch_data()  # TODO: unnecessary : remove when implemented
model = FrequencyModel(data)
winner = model.predict_winner('Tübingen', 'Leverkusen')
print(winner)
