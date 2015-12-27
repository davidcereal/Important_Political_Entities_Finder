import os

from collections import Counter

from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.index import open_dir

from fuzzywuzzy import fuzz



def search_topic(index, topic_string, year_start=20100101, year_end=20160101): 
    '''
    Function to search through the whoosh Index and return top matching results.
    
    Args:
        topic_string(str): The topic to search for amongst the articles
        year_start(int): The the starting point from which to keep results
        yeara_end(int): The ending point before which to keep results
    Returns:
        results(generator): A search result generator

    '''
    
    with index.searcher() as searcher:
        
        ## Create a query parser and define what it will parse
        qp = QueryParser("content", index.schema)                   
        query = qp.parse(topic_string)
        
        ## Create a date range filter 
        year_start = int(year_start)
        year_end = int(year_end)
        date_filter = qp.parse(u"date:[{} to {}]".format(year_start, year_end))
        
        ## Get results  
        results = searcher.search(query, filter=date_filter, limit=100)
        parsed_results = parse_results_into_top_counts(results)
    return parsed_results
        
def parse_results_into_top_counts(results):
    '''
    Function to take results from a search and perform a number of filters and parsers on 
    it. Lump together the most frequently mentioned named entities with their counts, combine 
    identical entities with slightly different names and then filter out the names of countries among them.
    
    Args:
        results(generator): A search result generator
    Returns:
        entities_list(list): A list of diectionaries where each dictionary contains the
        names and counts for a top-mentioned entity. 
    
    '''
    top_figures = {}
    top_figures_fuzzied = {'test':0}
    entities_list = []
    ## Add entities' to a dict and combine multiple entries
    for result in results:
        for entity, value in Counter(result['entities']).items(): 
            top_figures[entity]= top_figures.get(entity, 0) + value
            if entity.lower() in countries_list:
                 top_figures[entity]=0

    ## Create a list of most mentioned named entities
    sorted_top_figures = sorted(top_figures.items(), key=lambda (k, v): v, reverse=True)

    ## For each entity, compare it to other entitities using fuzzy ratio to
    ## combine identical entities that have slightly different names
    for item in sorted_top_figures[:50]:
        for key in top_figures_fuzzied.keys():
            if top_figures_fuzzied.has_key(item) == True:
                top_figures_fuzzied[key]= top_figures_fuzzied.get(key, 0)+ item[1]
            elif fuzz.ratio(item[0], key) > 76:
                top_figures_fuzzied[key]= top_figures_fuzzied.get(key, 0)+ item[1]
            else:
                top_figures_fuzzied[item[0]]= item[1]

    ## Filter out entities that are countries
    for k,v in top_figures_fuzzied.items():
        for country in countries_list:
            slot = 'unfilled'
            if fuzz.ratio(country, k.lower()) > 76:
                pass
        if slot != 'filled':
            entity_dictionary = {}
            entity_dictionary['name']= k
            entity_dictionary['size']= v
            entities_list.append(entity_dictionary)
            slot = 'filled'                 
    return entities_list



countries_list =[u'afghanistan',
 u'\xe5land islands',
 u'albania',
 u'algeria',
 u'american samoa',
 u'andorra',
 u'angola',
 u'anguilla',
 u'antarctica',
 u'antigua and barbuda',
 u'argentina',
 u'armenia',
 u'aruba',
 u'australia',
 u'austria',
 u'azerbaijan',
 u'bahamas',
 u'bahrain',
 u'bangladesh',
 u'barbados',
 u'belarus',
 u'belgium',
 u'belize',
 u'benin',
 u'bermuda',
 u'bhutan',
 u'bolivia',
 u'bonaire',
 u'bosnia and herzegovina',
 'bosnia',
 u'botswana',
 u'bouvet island',
 u'brazil',
 u'british indian ocean territory',
 u'brunei darussalam',
 u'bulgaria',
 u'burkina faso',
 u'burundi',
 u'cambodia',
 u'cameroon',
 u'canada',
 u'cape verde',
 u'cayman islands',
 u'central african republic',
 u'chad',
 u'chile',
 u'china',
 u'christmas island',
 u'cocos (keeling) islands',
 u'colombia',
 u'comoros',
 u'congo',
 u'congo, the democratic republic of the',
 u'cook islands',
 u'costa rica',
 u"c\xf4te d'ivoire",
 u'croatia',
 u'cuba',
 u'cura\xe7ao',
 u'cyprus',
 u'czech republic',
 u'denmark',
 u'djibouti',
 u'dominica',
 u'dominican republic',
 u'ecuador',
 u'egypt',
 u'el salvador',
 u'equatorial guinea',
 u'eritrea',
 u'estonia',
 u'ethiopia',
 u'falkland islands (malvinas)',
 u'faroe islands',
 u'fiji',
 u'finland',
 u'france',
 u'french guiana',
 u'french polynesia',
 u'french southern territories',
 u'gabon',
 u'gambia',
 u'georgia',
 u'germany',
 u'ghana',
 u'gibraltar',
 u'greece',
 u'greenland',
 u'grenada',
 u'guadeloupe',
 u'guam',
 u'guatemala',
 u'guernsey',
 u'guinea',
 u'guinea-bissau',
 u'guyana',
 u'haiti',
 u'heard island and mcdonald islands',
 u'holy see (vatican city state)',
 u'honduras',
 u'hong kong',
 u'hungary',
 u'iceland',
 u'india',
 u'indonesia',
 u'iran, islamic republic of',
 'iran',
 u'iraq',
 u'ireland',
 u'isle of man',
 u'israel',
 u'italy',
 u'jamaica',
 u'japan',
 u'jersey',
 u'jordan',
 u'kazakhstan',
 u'kenya',
 u'kiribati',
 'north korea',
 'south korea',
 'china',
 u"korea, democratic people's republic of",
 u'korea, republic of',
 u'kuwait',
 u'kyrgyzstan',
 u"lao people's democratic republic",
 u'latvia',
 u'lebanon',
 u'lesotho',
 u'liberia',
 u'libya',
 u'liechtenstein',
 u'lithuania',
 u'luxembourg',
 u'macao',
 u'macedonia',
 u'madagascar',
 u'malawi',
 u'malaysia',
 u'maldives',
 u'mali',
 u'malta',
 u'marshall islands',
 u'martinique',
 u'mauritania',
 u'mauritius',
 u'mayotte',
 u'mexico',
 u'micronesia, federated states of',
 u'moldova',
 u'monaco',
 u'mongolia',
 u'montenegro',
 u'montserrat',
 u'morocco',
 u'mozambique',
 u'myanmar',
 u'namibia',
 u'nauru',
 u'nepal',
 u'netherlands',
 u'new caledonia',
 u'new zealand',
 u'nicaragua',
 u'niger',
 u'nigeria',
 u'niue',
 u'norfolk island',
 u'northern mariana islands',
 u'norway',
 u'oman',
 u'pakistan',
 u'palau',
 u'palestine',
 u'panama',
 u'papua new guinea',
 u'paraguay',
 u'peru',
 u'philippines',
 u'pitcairn',
 u'poland',
 u'portugal',
 u'puerto rico',
 u'qatar',
 u'r\xe9union',
 u'romania',
 u'russian federation',
 'russia',
 'u.s.',
 'united states',
 u'rwanda',
 u'saint barth\xe9lemy',
 u'saint helena, ascension and tristan da cunha',
 u'saint kitts and nevis',
 u'saint lucia',
 u'saint martin (french part)',
 u'saint pierre and miquelon',
 u'saint vincent and the grenadines',
 u'samoa',
 u'san marino',
 u'sao tome and principe',
 u'saudi arabia',
 u'senegal',
 u'serbia',
 u'seychelles',
 u'sierra leone',
 u'singapore',
 u'sint maarten (dutch part)',
 u'slovakia',
 u'slovenia',
 u'solomon islands',
 u'somalia',
 u'south africa',
 u'south georgia and the south sandwich islands',
 u'spain',
 u'sri lanka',
 u'sudan',
 u'suriname',
 u'south sudan',
 u'svalbard and jan mayen',
 u'swaziland',
 u'sweden',
 u'switzerland',
 u'syrian arab republic',
 'syria',
 u'taiwan, province of china',
 u'tajikistan',
 u'tanzania, united republic of',
 u'thailand',
 u'timor-leste',
 u'togo',
 u'tokelau',
 u'tonga',
 u'trinidad and tobago',
 u'tunisia',
 u'turkey',
 u'turkmenistan',
 u'turks and caicos islands',
 u'tuvalu',
 u'uganda',
 u'ukraine',
 u'united arab emirates',
 u'united kingdom',
 u'united states',
 u'united states minor outlying islands',
 u'uruguay',
 u'uzbekistan',
 u'vanuatu',
 u'venezuela',
 u'viet nam',
 u'virgin islands, british',
 u'virgin islands, u.s.',
 u'wallis and futuna',
 u'western sahara',
 u'yemen',
 u'zambia',
 u'zimbabwe',
 'arab',
 'muslim',
 'jewish',
 'jew',
 'christian',
 'europe',
 'european',
 'asia',
 'asian',
 'africa',
 'america',
 'american',
 'south america',
 'north america',
 'russia'
 ]