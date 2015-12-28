"""
1. Store your Foreign Affairs login username and password. If you do not have an account, go to
https://www.foreignaffairs.com and register for free. 

Registered users without a subscription are entitled to 1 free article a month.
So, if you don't have a subscription, I suggest you run the flask visualization on its own. Doing so will utilize a
pre-built index comprised of 100 articles I scraped for this demo. 

2. Specify the number of articles to scrape.


3. Specify the location of the chromdriver. See the readme for further instructions on this. 
Example: /Users/David/Downloads/chromedriver

"""

## Specify your username and password:
login_username = "dberger1989@gmail.com"
login_password = "oliver4432"

## If you have a subcription, specify the number of articles to scrape:
n_articles_to_scrape = 100

## Specify path to the chromedriver
path_to_chromedriver = "/Users/David/Downloads/chromedriver"