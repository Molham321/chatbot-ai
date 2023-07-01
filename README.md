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
* (for production): MySQL Server 8.0 or higher

## Installing / Usage
* Open Project folder and run `pipenv install` at a console
    * This will create a virtual enviroment and install all dependencies from the pipfile

* Download nltk and spacy resources:
    * run `python -m nltk.downloader all`
    * run `python -m spacy download de_core_news_md`
    * Note that you might have to prepend `pipenv run` to run these commands inside our virtual environment in which the dependencies are installed.

* Configure .env
    * Rename `.env.development` or `.env.production` to `.env` 
    * Additional configuration for production:
      * you need a mysql database with a `my.cnf` (See [here](https://docs.djangoproject.com/en/4.2/ref/databases/#connecting-to-the-database))
        * Perform migration: `python manage.py migrate`
        * Create superuser (admin): `python manage.py createsuperuser`
      * you need to copy the static assets into the configured folder (`STATICFILES_DIR`)
        * use command: `python manage.py collectstatic`

## Authors
* **Abdul Samet Ankaoglu**
* **Andrej Bespalov**
* **Jan Kloß**
* **Christopher Lippek**
* **Christian Ortlepp**
* **Lukas Bachmann**
* **Sebastian Heine**

## Expanded by
* **Mohammad Shaheen**
* **Molham Al-Khodari**
* **Robin Beck**
* **Luca Voges**

## License

Copyright (C) Yggdrasil

All rights reserved.