# Important Political Entities Finder Overview

An app that allows users to seach for a topic in International Affairs and find out which political entities are most commonly associated with it. The corpus used is made up of articles scraped from the Foreign Affairs Magazine website. Check out the demo  <a href="http://107.23.92.220:5000" target="_blank">here</a>!


## 1. Clone the repository

```$ git clone https://github.com/dberger1989/Important_Political_Entities_Finder.git```

## 2. Setup

This code is portable across the following OS's: Linux distributions, Mac and Windows OS's. Scripts were written using Python 2.7 and have not been tested for portability to Python 3.X.

You are encouraged to use a python virtual environment using virtualenv and pip. 

```$ virtualenv venv```

### Install requirements:

```$ pip install -r requirements.txt```

#### Description of modules imported and application

* beautifulsoup4 - Beautiful Soup sits atop an HTML or XML parser, providing Pythonic idioms for iterating, searching, and modifying the parse tree.
* Flask - Flask is a microframework for Python based on Werkzeug, Jinja 2 and good intentions.
* 

## 3. Specify Foreign Affairs login and password credentials in config.py 

#### If you have a Foreign Affairs magazine subscription:
If you would have a subscription to Foreign Affairs magazine, you can put your username and password in the config.py file. 
Doing so will allow you to scrape as many articles as you please. 

You can specify how many articles to scrape in the config.py file. The default is set to 100. 

#### If you do not have a Foreign Affairs magazine subscription
If you don't have a subscription, you can still run the web-app. I have scraped 100 articles and preprocessed them. This way, you can skip the scraping and processing, and go straight to running the web-app on flask. To do this, skip to 
**Run the app without scraping new data**, in instruction #6. 

## 4. Install google's chromedriver:

Install from the website below using the appropriate link for your system:
	
```
http://chromedriver.storage.googleapis.com/index.html?path=2.19/
```

Specify the path to the downloaded chromedriver in the config.py file.  


## 5. Install NLTK dependencies:

```
$ python -m nltk.downloader all
```



## 6. Run Scraping, Analysis, and Visuzalization

#### Run the app without scraping new data:
To run the web-app using the pre-built index and avoid scraping altogether, run:
```
$ python important_political_entities_finder/visualize/app.py 
```

or:
### Run the full application:
Application can be run separately or all at once from a shell script.

#### To run separately:

```
$ python -m important_political_entities_finder.ingest.fa_scrape
$ python -m important_political_entities_finder.wrangle.parse_and_make_index
$ python important_political_entities_finder/visualize/app.py 
```

#### To run via shell script:

```$ source bin/important_political_entities_finder.sh```

## 7. Go to web-app!

The Flask app should be visible at the following location: 

``` http://127.0.0.1:5000/ ```
