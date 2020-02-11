# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Notebook example
#
# This is a small example for a notebook. Note we commit python code (`.py`) rather than notebooks (`.ipynb`), because is in many cases preferable for version control:
#
# - avoids blowing up the repository size by committing large often objects such as plots that are subject to change often
# - nicer diffs (better review)
# - allows direct execution of notebooks as .py files (which helps keeping your code cleaner)

# %matplotlib inline
# %load_ext autoreload
# %autoreload 2

import numpy as np
import matplotlib.pyplot as plt
plt.imshow(np.arange(4).reshape(2, 2))
