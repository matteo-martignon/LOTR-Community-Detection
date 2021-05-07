#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
result = requests.get("https://lotr.fandom.com/sitemap-newsitemapxml-index.xml")
c = result.content


# In[2]:


from bs4 import BeautifulSoup 
import lxml
import xml.etree.ElementTree as ET
root = ET.fromstring(c)
for link in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
    print(link.text)


# In[3]:


elements = dict()
for page in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
    result = requests.get(page.text)
    c = result.content
    new_root = ET.fromstring(c)
    for element in new_root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
        elements[element.text.split('/')[-1]] = element.text
print('Found {} elements'.format(len(elements)))


# In[4]:


characters_dict = {}
counter=0
for k,v in elements.items():
    result = requests.get(v)
    c = result.content
    soup = BeautifulSoup(c, "html.parser")  # parse HTML page 
    links = soup.find_all("div", class_='page-header__categories-links')
    try:
        if '/wiki/Category:Characters' in str(links[0]):
            characters_dict[k] = v
            counter+=1
            print('%s added to the dict, dict len: %s' %(k,str(len(characters_dict))))
    except:
        continue


# In[5]:


import json
with open('data.txt', 'w') as outfile:
    json.dump(characters_dict, outfile)


# In[6]:


category_dict={}
for k,v in characters_dict.items():
    if 'Category:' in k:
        category_dict[k]=v
len(characters_dict)


# In[7]:


for k in category_dict.keys():
    del characters_dict[k]


# In[8]:


len(characters_dict)


# In[9]:


inverted_dict = {v.encode(encoding='utf-8'): k for k, v in characters_dict.items()}


# In[10]:


import re
import collections
import pandas as pd


# In[11]:


character_count=collections.Counter()
character_text=dict()
character_network = collections.Counter()
base_url = 'https://lotr.fandom.com'

characters_details=[]

for character_url, character_name in inverted_dict.items():
    character_html = requests.get(character_url)
    
    soup = BeautifulSoup(character_html.content, "html.parser")
        
    lotr_dict={'character_name':character_name,'character_url': character_url}
    lotr_name = soup.find("h2", class_="pi-item pi-item-spacing pi-title")
    if lotr_name:
        lotr_dict['lotr_name']=lotr_name.contents[0]
    for lotr in soup.find_all("div", class_="pi-item"):
        lotr_data = lotr.text.split('\n')
        lotr_dict[lotr_data[1].strip().lower()] = lotr_data[2].strip().lower()
    characters_details.append(lotr_dict)
        
    character = {'name':character_name, 'url':character_url, 'html_content':character_html.text }    
    character['text'] = soup.find('div',{'id':'mw-content-text'}).text 
    try:
        character['links'] = collections.Counter([inverted_dict[str(base_url+link.get('href')).encode('utf-8')] for link in soup.find('div',{'id':'mw-content-text'}).find_all('a') if str(base_url+str(link.get('href'))).encode('utf-8') in re.findall(str(base_url+str(link.get('href'))+'\\b').encode('utf-8'),str(inverted_dict.keys()).encode('utf-8'))])
    except KeyError:
        character['links']=collections.Counter([])
    character_count=character_count + character['links']
    character_text[character_name]=soup.find("div",{"id":"mw-content-text"}).text
    for x in character:
        x = character_name
        for y in character['links']:
            character_network[(x, y)] = character['links'][y]
    print('%s added to the dict, dict len: %s' %(character_name,str(len(character_text))))


# In[16]:


l=[]
for i, j in character_network:
    l.append((i, j, character_network[i,j]))


# In[19]:


df = pd.DataFrame(l, columns=['source', 'target', 'weight'])


# In[29]:


df.to_csv('lotr_network.csv')


# In[27]:


pd.DataFrame(characters_details).to_csv('lotr_data.csv')

