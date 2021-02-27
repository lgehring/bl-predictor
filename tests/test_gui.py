from datetime import date

from bl_predictor import gui


def test_gui():
    try:
        tested_gui = gui.MainWindow("test")
    # detects headless server
    except:
        return None

    assert (tested_gui.picked_home_team is None)
    assert (tested_gui.picked_guest_team is None)
    assert (tested_gui.date_label.cget("text") == str(
        date.today().strftime("%a %d.%m.%y")))
    # timeframe slider
    assert (tested_gui.slider.W == 300)
    assert (tested_gui.act_crawler_button.cget("text")
            == "Download Data")
    # activate crawler
    tested_gui._activate_crawler_helper()
    assert (tested_gui.act_crawler_button.cget("text")
            == 'Download complete')
    assert tested_gui.crawler_data.empty is False
    tested_gui._choose_model()
    assert (tested_gui.model_label.cget(
        "text") == "Choose a prediction model:")
    # testing button to train model
    assert (tested_gui.train_ml_button.cget(
        "text") == "Train prediction model")
    tested_gui._train_model_helper()
    assert (tested_gui.train_ml_button.cget("text") == 'Model trained')
    # testing prediction button
    assert (tested_gui.prediction_button.cget("text")
            == "Show predicted winner!")
    tested_gui._make_prediction_helper()
    assert (tested_gui.prediction_button.cget("text")
            == 'Winner predicted')
    # testing reset teams button
    assert (tested_gui.reset_teams_button.cget("text")
            == "put in new teams")
    tested_gui._reset_teams()
    assert (not tested_gui.reset_teams_button.winfo_viewable())
    # testing reset model button
    assert (tested_gui.reset_model_button.cget("text")
            == "choose new model")
    tested_gui._reset_model()
    assert (not tested_gui.reset_model_button.winfo_viewable())
    # testing reset button
    assert (tested_gui.reset_button.cget("text")
            == "Reset")
    tested_gui._reset_model()
    assert (not tested_gui.reset_button.winfo_viewable())
