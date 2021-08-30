#!/usr/bin/env python
# coding: utf-8

# In[52]:


from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium import webdriver
from urllib.request import urlopen
from urllib.request import Request
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.common.keys import Keys
import re
import requests
import pandas as pd
from time import sleep


# In[53]:


file = pd.read_csv('C:/Users/USER/DA_Projects/Data_science_assignment_blackcoffer/cik_list.csv', nrows = 152 )


# In[54]:


list_SECFNAME = file['SECFNAME']


# In[55]:


list_SECFNAME


# In[56]:


#creating the generic stopwords list
stopwords_generic = io.open("StopWords_Generic.txt", "r")
list_stopwords_generic = []
for line in stopwords_generic:   
    list_stopwords_generic.append(line[:-1].lower())
print(list_stopwords_generic)


# In[57]:


#creating the auditor stopwords list
stopwords_auditor = io.open("C:/Users/USER/DA_Projects/Data_science_assignment_blackcoffer/StopWords_Auditor.txt", "r")
list_stopwords_auditor = []
for line in stopwords_auditor:   
    list_stopwords_auditor.append(line[:-1].lower())
print(list_stopwords_auditor)


# In[58]:


#creating the stopwords list for currencies and countries
stopwords_currencies = io.open("C:/Users/USER/DA_Projects/Data_science_assignment_blackcoffer/StopWords_Currencies.txt", "r")
list_stopwords_currencies = []
list_stopwords_countries = []
#country and currencies in the file are in the form of currency | country. split them on '|'. take the 1st half as currency  
#and other half as country
for line in stopwords_currencies:
    currency = line.split('|')[0]
    country = line.split('|')[1]
    list_stopwords_currencies.append(currency[:-1].lower())
    list_stopwords_countries.append(country[:-1].lower())
print(list_stopwords_currencies)
print(list_stopwords_countries)


# In[59]:


#Creating the stopwords list for dates and numbers
stopwords_currencies = io.open("C:/Users/USER/DA_Projects/Data_science_assignment_blackcoffer/StopWords_DatesandNumbers.txt", "r")
list_stopwords_DatesandNumbers = []
for line in stopwords_currencies:
    DatesandNumbers = line.split('|')[0]
    list_stopwords_DatesandNumbers.append(DatesandNumbers[:-1].lower())
print(list_stopwords_DatesandNumbers)


# In[60]:


#creating the stopwordc list of geographic 
stopwords_geographic = io.open("C:/Users/USER/DA_Projects/Data_science_assignment_blackcoffer/StopWords_Geographic.txt", "r")
list_stopwords_geographic = []
for line in stopwords_geographic:
    geographic = line.split('|')[0]
    list_stopwords_geographic.append(geographic[:-1].lower())
print(list_stopwords_geographic)


# In[61]:


#creating stop words list of common names
stopwords_names = io.open("C:/Users/USER/DA_Projects/Data_science_assignment_blackcoffer/StopWords_Names.txt", "r")
list_stopwords_names = []
for line in stopwords_names:
    names = line.split('|')[0]
    list_stopwords_names.append(names[:-1].lower())
print(list_stopwords_names)


# In[62]:


#creating list of some other generic stopwords
stopwords_genericlong = io.open("C:/Users/USER/DA_Projects/Data_science_assignment_blackcoffer/StopWords_GenericLong.txt", "r")
list_stopwords_genericlong = []
for line in stopwords_genericlong:  
    if len(line) <=3 or "'" in line:
        list_stopwords_genericlong.append(line[:-1].lower())
print(list_stopwords_genericlong)


# In[63]:


#read master dictionary file
master_dictionary = pd.read_csv('C:/Users/USER/DA_Projects/Data_science_assignment_blackcoffer/LoughranMcDonald_MasterDictionary_2020.csv')
words_list = list(master_dictionary['Word'])


# In[103]:


#function for calculating the 15 variables of a financial report
def calc_attributes(dict_words, df, word_len, table_dots_count, sentence_count):
    positive_score = 0
    negative_score = 0
    dict_values = list(dict_words.values())
    count = 0
    complex_words_count = 0
    uncertainty_count = 0
    constraining_count = 0
    #positive_list = list(df['Positive'])
    #negative_list = list(df['Negative'])
    #syllables_list = list(df['Syllables'])
    #calculating the avaerage sentence lenght.
    #before calculating it, check if the denominator falls to 0 in order to avoid divison by zero exception
    if (sentence_count - table_dots_count) != 0:
        average_sentence_length = word_len / (sentence_count - table_dots_count) 
    else:
        #if denominator is 0, set the average sentence length as 0
        average_sentence_length = 0
    for i in list(dict_words):
        #finding row in the master dictionery for each unique words present on a single financial report
        row = df[df['Word']== i.upper()]
        #finding the index value of that corresponding row
        #idx is an array with single element as index value
        idx = row.index.values
        #if idx array is empty, it means that, an element present on the report is not in the master dictioneary
        if len(idx) != 0:
            #index = idx[0]
            #dictkey_value gives the count of existence of each unique word in the report
            dictkey_value = dict_values[count]
            #calculating the positive score
            if row['Positive'].iloc[0] != 0:
                positive_score  += dictkey_value
            #calculating the positive score
            elif row['Negative'].iloc[0] != 0:
                negative_score += dictkey_value 
            
            #finding the count of syllables inorder to find if the word is complex or not
            if row['Syllables'].iloc[0] > 2:
                complex_words_count += dictkey_value
            
            #finding the count of uncertainty words
            if row['Uncertainty'].iloc[0] != 0:
                uncertainty_count += dictkey_value
            
            #finding the count of constraining words
            if row['Constraining'].iloc[0] != 0:
                constraining_count += dictkey_value
                
    polarity_score = (positive_score - negative_score)/((positive_score + negative_score)+(0.000001))
    #checking if the denominator is zero or not to avoid division by zero exception
    if word_len != 0:
        percentage_of_complex_words = complex_words_count / word_len
        positive_word_proportion = positive_score / word_len
        negative_word_proportion = negative_score / word_len
        uncertainty_word_proportion = uncertainty_count / word_len
        constraining_word_proportion = constraining_count / word_len
    else:
        percentage_of_complex_words = 0
        positive_word_proportion = 0
        negative_word_proportion = 0
        uncertainty_word_proportion = 0
        constraining_word_proportion = 0
    fog_index = 0.4 * (average_sentence_length + percentage_of_complex_words)
    return [positive_score, negative_score, polarity_score, average_sentence_length, percentage_of_complex_words, fog_index, complex_words_count, word_len, uncertainty_count, constraining_count, positive_word_proportion, negative_word_proportion, uncertainty_word_proportion, constraining_word_proportion]


# In[ ]:


import io
import nltk
from nltk.tokenize import RegexpTokenizer
from collections import Counter
i =0
count = 1
row =[]
rows = []
tokenizer = RegexpTokenizer('\w+')
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
while i < len(list_SECFNAME):
#while i < 1:
    words = []
    sentence_count = 0
    table_dots_count = 0
    url = "https://www.sec.gov/Archives/" + list_SECFNAME[i]
    #try:
        #page = requests.get(url, headers = headers)
        #break
    #except requests.exceptions.ConnectionError:
        #r.status_code = "Connection refused"
        #sleep(5)
    #make a request to a web page
    page = requests.get(url, headers = headers)
    #create a beautiful soup object
    soup = BeautifulSoup(page.text, 'html5')
    #finding tables elements by its tag
    tables = soup.find_all('table')
    #removing data inside all table tags. since it mostly contains names and digits
    for table_elem in tables:
        s = BeautifulSoup(str(table_elem))
        # match the opening tags, and any text after the first instance of < .*? non-greedily matches all text after the opening <, stopping at the first match of >
        pattern_2 = re.compile('<.*?>')
        # Use re.sub() to remove all tags and return only the text
        table_text = re.sub(pattern_2, '', str(table_elem))
        #counting the unwanted dots inside table tags
        table_dots_count += table_text.count('.')
    #finding all page elements by its tag
    elems = soup.find_all('page')
    #file_name = "financial report_"+ str(count)+".txt"
    #my_file = io.open(file_name, 'w', encoding = "utf-8")
    #print(file_name)
    for job_elem in elems:
        s = BeautifulSoup(str(job_elem))
        # match the opening tags, and any text after the first instance of < .*? non-greedily matches all text after the opening <, stopping at the first match of >
        pattern = re.compile('<.*?>')
        # Use re.sub() to remove all tags and return only the text
        base_text = re.sub(pattern, '', str(job_elem))
        #finding the sentences count inside the page elements by counting the number of '.'s
        sentence_count += base_text.count('.')
        #my_file.write(base_text)
        #my_file.write("\n\n")
        tokens = tokenizer.tokenize(base_text)
        #print(tokens)
        #token_file_name = "financial report_"+ str(count)+"_tokens.txt"
        #token_file = io.open(token_file_name, 'w', encoding = "utf-8")
        #for each tokens, checking whether if it present inside any stopword list
        for word in tokens:
            lower_word = word.lower()
            if not (lower_word in list_stopwords_generic or lower_word in list_stopwords_auditor or lower_word in list_stopwords_currencies or lower_word in list_stopwords_countries or lower_word in list_stopwords_DatesandNumbers or lower_word  in list_stopwords_geographic or lower_word  in list_stopwords_names or lower_word in list_stopwords_genericlong or lower_word[-1].isdigit()):
                #tokens other than stopwords are appending to the words list
                words.append(word.lower())
                #token_file.write(word.lower())
                #token_file.write("\n")
        token_file.close()
    #sorting the list based on number of times the word is mentioned in the report
    count_of_dist_words = dict(Counter(words))   
    word_len = len(words)
    row = calc_attributes(count_of_dist_words, master_dictionary, word_len, table_dots_count, sentence_count)
    rows.append(row)
    i+=1
    my_file.close()


# In[111]:


columns = ['positive_score', 'negative_score', 'polarity_score', 'average_sentence_length', 'percentage_of_complex_words', 'fog_index', 'complex_word_count', 'word_count', 'uncertainty_score', 'constraining_score', 'positive_word_proportion', 'negative_word_proportion', 'uncertainty_word_proportion', 'constraining_word_proportion']
output_file = pd.DataFrame(rows, columns=columns)


# In[112]:


output_file


# In[114]:


output_file.to_csv('report_attributes.csv', index = False)


# In[126]:


#result = file.copy()
result = pd.concat([file,output_file], axis=1, ignore_index=True)


# In[127]:


result


# In[128]:


result.to_csv('result.csv', index = False)


# In[ ]:




