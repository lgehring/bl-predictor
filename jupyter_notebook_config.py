# This integrates jupytext into jupyter notebooks/labs which allows
# automatically saving and loading notebooks as python code files or markdown
# documents (which in many cases is a better chocie for version control):
c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
