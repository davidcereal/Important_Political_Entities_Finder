import os
import time

from bs4 import BeautifulSoup
import requests

from selenium.webdriver.common.keys import Keys
from selenium import webdriver


from dateutil import parser



#-------------------------srape urls from archive----------------------------------------#

def recursive_click(element):
    '''
    Function to click on an element. If the click does not work, wait 10 
    seconds and try again. Useful for when selenium's Explicit Wait causes
    connection to close.
    
    '''
    try:
        element.click()
    except:
        time.sleep(10)
        recursive_click(element)




def get_article_links(path_to_chromedriver, n_articles_desired):
    '''
    Function to scrape the article htmls from the Foreign Affairs(FA) archive
    search page.'Load More' must be clicked each timeto get an additional 10 
    articles loaded to page. 
    
    Args:
        path_to_chromedriver(str): The path to where chromedriver is stored.
        n_articles_desired(int): The number of article urls to scrape
    Returns:
        soup(str): the html of the FA archive page with all the desired urls loaded.
    '''
    ## Foreign Affairs archive search page
    url = "https://www.foreignaffairs.com/search?qs="
    
    ## Load chromedriver
    chromedriver = path_to_chromedriver
    os.environ["webdriver.chrome.driver"] = chromedriver
    
    ## Use driver to load FA archive page
    driver = webdriver.Chrome(chromedriver)
    driver.get(url)
    
    ## Click on date button to sort articles in descending date order
    date_reverse = driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div[2]/div/div/div/a')
    recursive_click(date_reverse)
    
    ## Each time 'load more' is clicked, 10 more articles are
    ## listed. Determine how many times to click 'Load More'
    if n_articles_desired <= 10:
        loads_needed = 1
    else:
        loads_needed = n_articles_desired/10

    for i in range(loads_needed):
        ## Click the 'Load More' button 
        load_more =  driver.find_element_by_link_text("Load More")
        recursive_click(load_more)
        
    ## Return the html for the page with all the articles listed
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup


    
    



if __name__ == "__main__":
    main()