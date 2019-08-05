#!/usr/bin/env python
# coding: utf-8

# # 10페이지 넘어가는 경우 해결
# # 저장 구조 바꾸기, 제목, 언론사, 날짜 전부 저장하기

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


press_dict = {'경향신문' : '032' , '국민일보' : '005', '동아일보' : '020', '문화일보' : '021', '서울신문' : '081', '세계일보' : '022', '조선일보' : '023', '중앙일보' : '025', '한겨레' : '028', '한국일보' : '469'}


# In[3]:


wd = "./chromedriver"
driver = webdriver.Chrome(wd)


# In[17]:


print('크롤링을 원하는 언론사를 입력.')
test_press = input()

if test_press in press_dict.keys():
    get_number = press_dict[test_press]
    print('원하는 날짜를 입력')
    test_date = input()
    puzzle_url = 'https://news.naver.com/main/list.nhn?mode=LPOD&mid=sec&oid=' + get_number + '&date=' + test_date
    print('{}의 {}날짜 뉴스를 크롤링합니다.'.format(test_press, test_date))
else:
    print('입력한 언론사가 리스트에 없습니다. https://news.naver.com/main/officeList.nhn 에 들어가서 원하는 언론사의 url을 입력해주세요.')
    puzzle_url = input()
    driver.get(puzzle_url)
    input_now = driver.page_source
    input_source = BeautifulSoup(input_now, 'lxml')
    page_list = input_source.find_all('div', {'class' : 'newsflash_header3'})
    press_now = page_list[0].h3.text
    print('{} 맞나요? 원하는 날짜를 입력(yyyymmdd).'.format(press_now))
    test_date = input()
    print('{}의 {}날짜 뉴스를 크롤링합니다.'.format(press_now, test_date))
    puzzle_url = puzzle_url+ '&date=' + test_date
    


# In[18]:


driver.get(puzzle_url)


# In[19]:


tmp = driver.current_url


# In[20]:


page_now = driver.page_source
page_now = BeautifulSoup(page_now, 'lxml')
page_list = page_now.find_all('a', {'class' : 'nclicks(fls.page)'})
page_length = len(page_list)


# In[9]:


count = 0


# In[10]:


for i in range(page_length+1):
    
    page_url = tmp + '&page=' + str(i+1)
    driver.get(page_url)
    
    today_html = driver.page_source
    listup = BeautifulSoup(today_html, 'lxml')

    news_list = listup.find_all('a', {'class' : 'nclicks(cnt_papaerart)'})
    news_list += listup.find_all('a', {'class' : 'nclicks(cnt_papaerart3)'})
    news_list += listup.find_all('a', {'class' : 'nclicks(cnt_papaerart4)'})
    news_list += listup.find_all('a', {'class' : 'nclicks(cnt_flashart)'})


    for index in range(len(news_list)):
    
        count += 1

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


# In[11]:


print('number of articles: {}'.format(count))


# with open('./정치/한겨레_2019.07.28._넉달째맹탕국회…정치가없다.json', encoding = 'utf-8') as f:
#     data = json.load(f)
#     df = pd.DataFrame({'comment' : data['comment'], 'like':data['like'], 'dont_like':data['dont_like']})

# data['contents']

# df.head(100)

# In[ ]:




