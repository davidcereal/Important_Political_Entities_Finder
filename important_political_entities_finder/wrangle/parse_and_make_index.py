import pickle

import os
import shutil

from collections import Counter

import nltk
from nltk.tag import pos_tag
from nltk import ne_chunk
from nltk import word_tokenize
from nltk import maxent
from nltk import Tree

from fuzzywuzzy import fuzz

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.index import open_dir




class Make_index(object):

    def __init__(self):

        with open('important_political_entities_finder/ingest/data_store/articles_data_list.pkl', 'r') as picklefile:
            self.articles_data_list = pickle.load(picklefile)

    def extract_entity_names(self, text):
        '''
        Function to extract the named entities (NE) from a text.
        
        Args:
            text(str): A string containing body of text
        Returns:
            entity_names: 
            
        '''
        entity_names = []
        if hasattr(text, 'label') and text.label:
            if text.label() == 'NE':
                entity_names.append(' '.join([child[0] for child in text]))
            else:
                for child in text:
                    entity_names.extend(extract_entity_names(child))

        return entity_names

    def parse_and_add_named_entites(self, articles_data_list):
        '''
        Function that iterates through a list of article data dictionaries and
        parses the text of the articles for named entities and adds them as an entry
        to the dictionary.
        
        Args: 
            articles_data_list(list): a list of article dictionaries
        Returns:
            None
        '''
        
        for article in articles_data_list:

            ## Tokenize words of the text
            tokenized = word_tokenize(article['text'])

            ## Tag the part of speach for each word
            tagged_words = pos_tag(tokenized)

            ## Chunk the words together based on pos
            chunked_sentences = nltk.ne_chunk(tagged_words, binary=True) 

            ## Extract the entity names from the text 
            entity_names = []
            for tree in chunked_sentences:
                entity_names.extend(self.extract_entity_names(tree))

            ## Add to dictionary
            article['named_entities'] = entity_names

    def create_index(self, articles_data_list):
        '''
        Function to make a searchable whoosh index out of the corpus of article data. Creates an 
        Index folder in current directory. 
        
        Args:
            articles_data_list(list): a list of article dictionaries
        Returns:
            none

        '''
        ## Make schema of what should be the search criteria and whether it should be stored in results
        schema = Schema(title=TEXT(stored=True), date=DATETIME, path=ID(stored=True), content=TEXT, entities=TEXT(stored=True))

        ## Make index folder to store index of articles text. Overwrite if exists.
        dir = "important_political_entities_finder/wrangle/index"
        if not os.path.exists(dir):
            os.makedirs(dir)
        else:
            shutil.rmtree(dir)         
            os.makedirs(dir)

        ## Create index in 'index' folder with schema structure
        ix = create_in("important_political_entities_finder/wrangle/index", schema)

        ## Create writer object to add articles to index
        writer = ix.writer()

        ## Add article text, headlines, entity counts, and dates as documents in Index
        for article in articles_data_list:    
            writer.add_document(title=unicode(article['title']), 
                                content=unicode(article['text']),
                                date = article['date'],
                                entities = article['named_entities']
                                )
        ## Commit the documents to the index folder
        writer.commit()

    def main(self):

        print "parsing entities.."
        self.parse_and_add_named_entites(self.articles_data_list)
        
        print "making index..."
        self.create_index(self.articles_data_list)
        
        print "index creation complete"




    
    
if __name__ == "__main__":
    Make_index().main()

