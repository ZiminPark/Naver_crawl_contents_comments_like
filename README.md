# Naver_crawl_contents_comments_like
네이버 뉴스에서 특정 언론사 하루치 기사의 제목, 날짜, 내용, 댓글, 좋아요, 싫어요 data를 수집합니다.


## Requirements
bs4, selenium, webdriver(참고 : https://blog.pignu.kr/2018/03/26/naver_crawling.html)

chromedriver.exe가 같은 폴더에 있어야 합니다.

## 실행 방법
```
python naver_news_crawling.py 100  # 댓글을 몇개나 크롤링할지 뒤에 인자에 넣어줍니다.
```

https://news.naver.com/main/officeList.nhn

위의 링크로 들어가 보면 언론사 별로 하루 뉴스를 모아둔 리스트를 볼 수 있습니다.

언론사의 하루 뉴스를 '분류+언론사+날짜+제목.json' 형태로 저장합니다.

json에는 url, 언론사, 날짜, 분류, 제목, 기사내용, 댓글, 공감수, 비공감수가 저장됩니다.

공감수별로 정렬이 가능한 언론사는 공감수 순서대로 댓글이 수집됩니다.


## 참고

- 스포츠와 연예 기사는 제외 했음. (구조가 다름)

- 에러가 있는 기사는 넘어감.
          
## 파일 읽는 예시 (encoding 해줘야 함.):

```
    with open('./한겨레/정치_한겨레_2019.07.28._넉달째맹탕국회…정치가없다.json', encoding = 'utf-8') as f:
        data = json.load(f)
        df = pd.DataFrame({'comment' : data['comment'], 'like':data['like'], 'dont_like':data['dont_like']})
```
