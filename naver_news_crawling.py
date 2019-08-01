#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os.path
import re
import selenium
import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import exceptions
import json
from collections import OrderedDict
import sys


# In[2]:


wd = "./chromedriver"
driver = webdriver.Chrome(wd)


# In[3]:


driver.get(sys.argv[1])
today_html = driver.page_source
listup = BeautifulSoup(today_html, 'lxml')


# In[ ]:


news_list = listup.find_all('a', {'class' : 'nclicks(cnt_papaerart)'})
news_list += listup.find_all('a', {'class' : 'nclicks(cnt_papaerart3)'})
news_list += listup.find_all('a', {'class' : 'nclicks(cnt_papaerart4)'})
news_list += listup.find_all('a', {'class' : 'nclicks(cnt_flashart)'})


# In[ ]:


for index in range(len(news_list)):
    
    addr = news_list[index]['href']
    driver.get(addr)
    
    # 스포츠 뉴스와 연예 뉴스는 제외 (형식도 다르고 목적과 맞지 않음.)
    check = driver.current_url
    if ('sports' in check) or ('entertain' in check):
        continue
        
    html = driver.page_source

    # 타이틀, 분류, 날짜, 언론사, 내용, 댓글 
    dom = BeautifulSoup(html, 'lxml')
    
    category_raw = dom.find('em', {'class' : 'guide_categorization_item'})
    category = category_raw.text

    title_raw = dom.find_all('h3', {'id' : 'articleTitle'})
    title = [title.text for title in title_raw]
    title = str(title[0])
    
    # 저장시 문제 안생기게
    title = re.sub("\"",'',title)
    title = re.sub("\'",'',title)
    title = re.sub("‘",'',title)
    title = re.sub("’",'',title)
    title = re.sub(" ",'',title)
    title = re.sub("\?",'',title)
    title = re.sub(":",'',title)
    title = re.sub("\/",'',title)

    date_raw = dom.find_all('span', {'class' : 't11'})
    date = date_raw[0].text.split()[0]

    press_raw = dom.find('div', {'class' : 'press_logo'})
    press = press_raw.select('a')[0].find('img')['title']

    category_raw = dom.find('em', {'class' : 'guide_categorization_item'})
    category = category_raw.text

    contents_raw = dom.find('div', {'id' : 'articleBodyContents'})
    contents = contents_raw.text

    # 네이버 뉴스에는 아래와 같은 주석이 항상 있음. 이 주석을 제거하기 위한 코드
    # \n\n\n\n\n// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}\n\n 
    clean_index = contents.index('removeCallback') + 23
    contents = contents[clean_index :]


    # 기사 포맷이 거의 항상 아래와 같음. 필요 없는 정보를 제거하기 위한 코드
    # [ⓒ한겨레신문 : 무단전재 및 재배포 금지]
    if '재배포' in contents:
        reporter_index = contents.index('재배포') - 15
        contents = contents[:reporter_index]

    time.sleep(0.2)
    pages = 0
    
    try:
        driver.find_element_by_css_selector(".u_cbox_in_view_comment").click()
        time.sleep(0.2)
    except exceptions.ElementNotInteractableException as e:
        pass
    except exceptions.NoSuchElementException as e:
        try:
            new_addr = dom.find_all('div', {'class' : 'simplecmt_links'})
            new_addr = new_addr[0].select('a')[0]['href']
            driver.get(new_addr)
            time.sleep(0.2)
        except:
            pass
        pass
    
    try:
        driver.find_element_by_css_selector(".u_cbox_sort_label").click()
        time.sleep(0.2)
    except exceptions.NoSuchElementException as e:
        pass
 
    i = 0

    try:
        while i < 30 :
            driver.find_element_by_css_selector(".u_cbox_btn_more").click()
            time.sleep(0.1)
            i+=1

    except exceptions.ElementNotVisibleException as e: # 페이지 끝
        pass

    except Exception as e: # 다른 예외 발생시 확인
        print(e)

    html = driver.page_source
    dom = BeautifulSoup(html, 'lxml')
    
    comments_raw = dom.find_all('span', {'class' : 'u_cbox_contents'})
    comments = [comment.text for comment in comments_raw]
    
    if (len(comments)<1):
        continue

    like_comments_raw = dom.find_all('em', {'class' : 'u_cbox_cnt_recomm'})
    like_comments = [int(like.text) for like in like_comments_raw]

    hate_comments_raw = dom.find_all('em', {'class' : 'u_cbox_cnt_unrecomm'})
    hate_comments = [int(hate.text) for hate in hate_comments_raw]
    
    df = pd.DataFrame({'comment' : comments, 'like' : like_comments, 'dont_like' : hate_comments})
    df = df.sort_values(by = 'like', ascending = False)
    
    file_name = './'+ category+ '/' + press+'_'+date+'_'+title + '.json'

    file_data = OrderedDict()
    file_data['contents'] = contents
    file_data['comment'] = df['comment'].values.tolist()
    file_data['like'] = df['like'].values.tolist()
    file_data['dont_like'] = df['dont_like'].values.tolist()
    
    directory = './' + category

    if os.path.exists(directory):
        with open(file_name, 'w', encoding = 'utf-8') as make_file:
            json.dump(file_data, make_file, ensure_ascii=False, indent='\t')

    else:
        os.mkdir(directory)
        with open(file_name, 'w', encoding = 'utf-8') as make_file:
            json.dump(file_data,  make_file,ensure_ascii=False, indent='\t')


# In[ ]:


with open('./정치/한겨레_2019.07.28._넉달째맹탕국회…정치가없다.json', encoding = 'utf-8') as f:
    data = json.load(f)
    df = pd.DataFrame({'comment' : data['comment'], 'like':data['like'], 'dont_like':data['dont_like']})


# In[ ]:


data['contents']


# In[ ]:


df.head(100)


# In[ ]:




