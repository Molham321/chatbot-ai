# FH-Erfurt AI Chatbot
This repository is used for the FHE-AI Chatbot implementation. 

## Project Setup
* Git installed
    * [Git download](https://git-scm.com/downloads)
* Django 3.1
* Python 3.8.x **64-bit**
    * [Python Download](https://www.python.org/downloads/)
        * Get the 64-Bit version ! (needed for the spacy package)
    * Make sure to "add python to enviroment variables" (Checkbox while installation)
* pipenv installed
    * [pipenv](https://pypi.org/project/pipenv/)
    * `pipenv run` before each command to run commands within the virtual enviroment
* Working with Django REST Framework


## Installing / Usage
* Open Project folder and run `pipenv install` at a console
    * This will create a virtual enviroment and install all dependencies from the pipfile

* Download nltk and spacy resources:
    * run `python -m nltk.downloader all`
    * run `python -m spacy download de_core_news_md`
    * Note that you might have to prepend `pipenv run` to run these commands inside our virtual environment in which the dependencies are installed.


## Authors
* **Abdul Samet Ankaoglu**
* **Andrej Bespalov**
* **Jan Kloß**
* **Christopher Lippek**
* **Christian Ortlepp**
* **Lukas Bachmann**
* **Sebastian Heine**

## License

Copyright (C) Yggdrasil

All rights reserved.