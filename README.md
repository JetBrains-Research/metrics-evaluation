# Evaluation of metrics for code generation
This repository will contain code to run the existing approaches to code generation on multiple datasets.

## Labeling the CoNaLa data
To participate in the CoNaLa data labeling, please follow these steps:
* Clone the repository: `git clone https://github.com/JetBrains-Research/metrics-evaluation.git`
* (optional) Set up a virtual environment: `virtualenv venv && source venv/bin/activate` 
* Install required packages: `pip install -r requirements.txt`
* Run `python rate.py --filename to-grade/all-singles.json`
* Follow the instructions in CLI!
* When you are finished, send us your `to-grade/all-singles.json` or `to-grade/all-singles.tmp.json` file.
* Any contribution is very-very valuable, so don't hesitate to send the files with any amount of labels!

## Labeling the Hearthstone data
To participate in the Hearthstone data labeling, please follow these steps:
* Clone the repository: `git clone https://github.com/JetBrains-Research/metrics-evaluation.git`
* (optional) Set up a virtual environment: `virtualenv venv && source venv/bin/activate`
* Install required packages: `pip install -r requirements.txt`
* Run `python hs-rate.py`
* Follow the instruction in the app!
* After you have graded several examples, please check if the to-grade/hs.tmp.json file has been created; if it is absent, please contact Misha
* When you are finished, send us your `to-grade/hs.json` or `to-grade/hs.tmp.json` file.
* Any contribution is very-very valuable, so don't hesitate to send the files with any amount of labels!

