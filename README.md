This is a Python implementation of a simple search engine.
Currently, the data we are using is available in 
[this cloud bucket](https://storage.googleapis.com/data2040-data/data.zip).

All code to be implemented during TA camp is in `core.py`. 

## Todo
- Make this repository private
- Improve handouts for all assignments
- Create robust solutions for all assignments
- Share the Google Cloud project with team members
- Add these todos to the Trello board


## Setting up on Pycharm

Configure your PyCharm settings by following the instructions below:

1. File -> Default settings -> Project Interpreter -> Pick a version of Python 3.6 -> OK
2. Settings -> Project:solution -> Project Interpeter -> Settings icon -> Create virtual env
-> name virtual environment, pick 3.6 -> OK
3. Alt-F12 to open the terminal in Pycharm
4. pip install -r requirements.txt

## Contributing

All of our code is currently in the file `core.py`. Tests are in `test_core.py`. Issues are posted
on the GitHub.

The process for fixing issues is as follows:

1. Create an issue on GitHub if necessary.
2. Run `tox` from the root workspace directory.
3. If all tests pass, you are good to push to the `master` branch.
4. Close the corresponding issue(s).

If implementing a larger feature (>100 LOC), create a new branch open up a pull request. We
recommend that you keep your commits modular.



