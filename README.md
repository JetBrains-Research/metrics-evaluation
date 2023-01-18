# Evaluation of metrics for code generation
This repository will contain code to run the existing approaches to code generation on multiple datasets.

## Setup

We use poetry to manage the environment and library versions. You can find the installation manual [here](https://python-poetry.org/docs/).

To run grading scripts you will also need to install `tkinter`. 
For linux users: `sudo apt-get install python3-tk`. 
For Mac users: `brew install python-tk@3.9`

## Labeling the CoNaLa data
To participate in the CoNaLa data labeling, please follow these steps:
* Clone the repository: `git clone https://github.com/JetBrains-Research/metrics-evaluation.git`
* (optional) Set up a virtual environment: `virtualenv venv && source venv/bin/activate` 
* Install required packages: `pip install -r requirements.txt`
* Run `python rate.py`. **NB:** Please run the labeling script with Python, and not from your IDE, as the latter way may not work
* Follow the instructions in CLI!
* When you are finished, send us your `to-grade/all-singles.json` or `to-grade/all-singles.tmp.json` file.
* Any contribution is very valuable, so don't hesitate to send the files with any amount of labels!

## Labeling the Hearthstone data
To participate in the Hearthstone data labeling, please follow these steps:
* Clone the repository: `git clone https://github.com/JetBrains-Research/metrics-evaluation.git`
* (optional) Set up a virtual environment: `virtualenv venv && source venv/bin/activate`
* Install required packages: `pip install -r requirements.txt`
* Run `python hs-rate.py`
* In case the app doesn't run, you may need to install package `tkinter` system-wide (please get in touch if further instructions are needed)
* Follow the instruction in the app!
* The description of the used classes can be found at https://github.com/danielyule/hearthbreaker/blob/master/hearthbreaker/cards/base.py
* After you have graded several examples, please check if the to-grade/hs.tmp.json file has been created; if it is absent, please contact Misha
* When you are finished, send us your `to-grade/hs.json` or `to-grade/hs.tmp.json` file.
* Any contribution is very valuable, so don't hesitate to send the files with any amount of labels!
