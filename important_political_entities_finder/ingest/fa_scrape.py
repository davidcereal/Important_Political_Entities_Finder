#!/usr/bin/env python
import os
import time
import pickle

from bs4 import BeautifulSoup
import requests

from selenium.webdriver.common.keys import Keys
from selenium import webdriver

from dateutil import parser
import re

import config




class FA_scrape(object):

    def __init__(self):

        ## FA login placeholders that must be filled in by users.
        LOGIN_USERNAME = config.login_username
        LOGIN_PASSWORD = config.login_password

        self.login_username = LOGIN_USERNAME
        self.login_password = LOGIN_PASSWORD

        ## Placeholder for number of articles to scrape that must be filled in by users.
        N_ARTICLES_TO_SCRAPE = config.n_articles_to_scrape
        self.n_articles_to_scrape = N_ARTICLES_TO_SCRAPE
        
        ## Placeholder for path to chromedriver that must be filled in by users
        PATH_TO_CHROMEDRIVER = config.path_to_chromedriver
        self.chromedriver = PATH_TO_CHROMEDRIVER
        
        ## Use driver to load FA archive page
        self.driver = webdriver.Chrome(self.chromedriver)
    #-------------------------load and scrape archive page------------------------------------#
    def get_article_links(self, n_articles_to_scrape, driver):
        '''
        Function to scrape the article htmls from the Foreign Affairs(FA) archive
        search page.'Load More' must be clicked each timeto get an additional 10 
        articles loaded to page. 
        
        Args:
            n_articles_to_scrape(int): The number of article urls to scrape
            driver(selenium webdriver obj): The chromedriver object
        Returns:
            url_archive_html_soup(str): the html of the FA archive page with all the desired urls loaded.
        '''
        ## Foreign Affairs archive search page
        url = "https://www.foreignaffairs.com/search?qs="
        
        driver.get(url)
        
        ## Click on date button to sort articles in descending date order
        self.recursive_click(driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div[2]/div/div/div/a'))
        
        ## Each time 'load more' is clicked, 10 more articles are
        ## listed. Determine how many times to click 'Load More'
        if n_articles_to_scrape <= 10:
            loads_needed = 1
        else:
            loads_needed = n_articles_to_scrape/10

        for i in range(loads_needed):
            ## Click the 'Load More' button 
            self.recursive_click(driver.find_element_by_link_text("Load More"))
            
        ## Return the html for the page with all the articles listed
        url_archive_html_soup = BeautifulSoup(driver.page_source, 'html.parser')
        return url_archive_html_soup

    def place_urls_in_list(self, url_archive_html, n_articles_to_scrape):
        '''
        Function to find all the urls in the scraped archive page and then
        store them in a list. 
        
        Args:
            url_archive_html_soup(Beautiful Soup obj): A Beautiful Soup html object of the Foreign Affairs archive page 
            containing the urls of the articles
        Returns:
            article_links:
                A list of urls
                
        '''
        article_links = []
        article_titles = url_archive_html.find_all(class_='title')
        for item in article_titles:
            href_string = item.contents[1]
            for href_tag, link_extension in href_string.attrs.items():
                full_link = "https://www.foreignaffairs.com" + link_extension
                article_links.append(full_link)
        article_links = article_links[:n_articles_to_scrape]
        print "---links to scrape:----"
        for link in article_links:
            print link
        print "-----------------------"
        return article_links

    #-------------------------scrape data from article pages------------------------------------#

    def login_get_article_text(self, article_url, login_username, login_password, driver):
        '''
        Function to login to Foreign Affairs(FA) website, should user be prompted to do so.
        
        Args:
            article_url(str): url of the article
            login_username(str): FA login username
            login_password(str): FA password
        Returns:
            article_html_soup(Beautiful Soup obj): The html of the article


        '''

        ## Click to login
        login = driver.find_element_by_xpath('//*[@id="content"]/article/div[3]/div[2]/div[1]/div/div[1]/div/a[1]')
        login.click()
        time.sleep(5)

        ## Locate email and password fields
        email_address_username = driver.find_element_by_xpath('//*[@id="edit-name"]')
        password = driver.find_element_by_xpath('//*[@id="edit-pass"]')
        
        ## Click on the date button to reverse order of dates displayed so they are descending
        email_address_username.send_keys(login_username)
        password.send_keys(login_password)
        time.sleep(5)
        ## Submit
        submit = driver.find_element_by_xpath('//*[@id="edit-submit--3"]')
        submit.click()
         
        time.sleep(5)    
        ## Make soup out of page_source
        page_source = driver.page_source
        article_html_soup = BeautifulSoup(driver.page_source, 'html.parser')
        return article_html_soup


    def get_article_text_no_login(self, article_url, driver):
        '''
        Function to load article page if there is no login needed
        '''
        page_source = driver.page_source
        article_html_soup = BeautifulSoup(driver.page_source, 'html.parser')
        return article_html_soup
        

    def get_article_data(self, article_links, driver):
        '''
        Function to get the data for each article from the list of article links.
        The data to be scraped for each article is the title, description, date, and text.
        Stores each articles as a document in a mongoDB database.
        
        Args:
            article_links(list): a list of article urls
            driver(selenium webdriver obj): The chromedriver object
        Returns:
            articles_data_list(list): A list of dictionaries where each dictionary contains the title,
            description, date, and text of each article.
            
        '''
        articles_data_list = []
        for article_url in article_links:
            ## Go to article page
            driver.get(article_url)
            time.sleep(5)

            ## Check if login needed
            try:
                driver.find_element_by_xpath('//*[@id="content"]/article/div[3]/div[2]/div[1]/div/div[1]/div/a[1]')
                soup = self.login_get_article_text(article_url, self.login_username, self.login_password, driver)
            
            ## If not needed
            except:
                soup = self.get_article_text_no_login(article_url, driver)
            
            ## Retrieve the top and bottom halves of the article
            top_content = soup.find_all(class_="top_content_at_page_load" )
            end_content = soup.find_all(class_="l-article-column article-icon-cap")

            ## Format out the unicode from the top half
            try:
                top_article_formatted = self.remove_unwanted_unicode_characters(top_content[0].get_text())
            except:
                top_article_formatted = soup.findAll(class_="container l-detail")[0].text

            ## Format out the unicode from the bottom half
            try:
                bottom_article_formatted = self.remove_unwanted_unicode_characters(end_content[0].get_text())
            except:
                bottom_article_formatted = 'blank'

            ## Combine top and bottom halves
            full_article = top_article_formatted + " " + bottom_article_formatted

            ## Get headline tag and convert to string
            title_tag = soup.find_all(class_="article-header__headline")[0].contents[0]
            title = self.remove_unwanted_unicode_characters(title_tag)
            ## Get headline tag and convert to string
            try:
                description_tag = soup.find_all(class_='article-header__deck')[0].contents[0]
                description = self.remove_unwanted_unicode_characters(description_tag)
            except:
                description = 'blank'

            ## Get article date
            try:
                date = parser.parse(str(soup.findAll('time')[0].contents[0]))
            except:
                try:
                    date = parser.parse(re.findall('([0-9]{4}-[0-9]{2}-[0-9]{2})', concatenated_url)[0])
                except: 
                    try:
                        date = str(soup.findAll(class_='date')[0].contents[0])
                        date = parser.parse(re.findall('/.+', date)[0])
                    except:
                        date = str(soup.find(class_="article-header__metadata-date").text)
                        date = parser.parse(re.findall('/\w+\s{1}\d+', date)[0])

            ## Make a dictionary out of the article data
            article_data_dic = dic = {'title':title, 'date':date, 
                                      'description':description, 'text':full_article }

            ## Append the dictionary of article data to a list with the other article data
            articles_data_list.append(article_data_dic)
        return articles_data_list


    #-------------------------helper functions------------------------------------#

    def recursive_click(self, path_to_element):
        '''
        Function to click on an element. If the click does not work, wait 10 
        seconds and try again. Useful for when selenium's Explicit Wait causes
        connection to close.
        
        Returns:
            None
        '''
        try:
            path_to_element.click()
        except:
            time.sleep(10)
            self.recursive_click(path_to_element)

    def remove_unwanted_unicode_characters(self, text_string):
        '''
        Function to get rid of unwanted unicode.

        '''
        new_text_string = re.sub(u"(\u2018|\u2019)", "'", text_string)
        new_text_string = re.sub(u"(\u2014)", "--", new_text_string)
        new_text_string = re.sub(u"(\u201c|\u201d)", '"' , new_text_string)
        new_text_string = re.sub(u"(\xa0)", "", new_text_string)
        new_text_string = new_text_string.replace("\n","")
        new_text_string = re.sub(u"(\u2013)", "-", new_text_string)
        new_text_string = re.sub(u"(\u2026)", "...", new_text_string)
        new_text_string = re.sub(u"(\xe9)", "e", new_text_string)
        new_text_string = re.sub(u"(\xad)", "-", new_text_string)
        new_text_string = re.sub(u"(\xfa)", "u", new_text_string)
        new_text_string = re.sub(u"(\xf3)", "o", new_text_string)
        new_text_string = re.sub(u"(\xed)", "i", new_text_string)
        new_text_string = re.sub(u"(\xe3)", "a", new_text_string)
        #new_text_string = re.sub(u"(\u2026)", "...", new_text_string)
        #new_text_string = re.sub(u"(\u2026)", "...", new_text_string)
        #new_text_string = re.sub(u"(\u2026)", "...", new_text_string)
        new_text_string = str(new_text_string.encode('ascii','ignore')).replace("\\","")
        #new_text_string = re.sub("\\", "", str(new_text_string))
        return new_text_string

    def main(self):

        print "scraping article urls..."
        ## Get the html with the links to the the last n articles from
        ## the Foreign Affairs website
        url_archive_html_soup = self.get_article_links(self.n_articles_to_scrape, self.driver)

        ## Get article links from url archive html
        article_links = self.place_urls_in_list(url_archive_html_soup, self.n_articles_to_scrape)

        print "scraping article data..."
        ## Iterate throgh concatenated urls and get article data from the page
        articles_data_list = self.get_article_data(article_links, self.driver)

        print "pickling article data..."
        with open('important_political_entities_finder/ingest/data_store/articles_data_list.pkl', 'w') as picklefile:
            pickle.dump(articles_data_list, picklefile)
        print "scraping complete"




    
    



if __name__ == "__main__":
    FA_scrape().main()
