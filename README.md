# naver_crawl_contents_comments_like
네이버 뉴스에서 특정 언론사 하루치 기사의 제목, 날짜, 내용, 댓글, 좋아요, 싫어요 data를 수집합니다.

# 필요한 모듈
bs4, selenium, webdriver(참고 : https://blog.pignu.kr/2018/03/26/naver_crawling.html) 설치해야 합니다.
chromedriver.exe가 같은 폴더에 있어야 합니다.

# 실행 방법
```
python naver_news_crawling_py_version.py "https://news.naver.com/main/list.nhn?mode=LPOD&mid=sec&oid=025&date=20190715"
```

https://news.naver.com/main/list.nhn?mode=LPOD&mid=sec&oid=032

위의 링크로 들어가 보면 신문사 별로 하루 뉴스를 모아둔 리스트를 볼 수 있습니다.

"위의 링크" + "&date=20190715" 이런 식으로 날짜를 지정할 수 있습니다.

이 리스트 중 첫 번째 페이지의 기사들을 크롤링 해서  ' 언론사+날짜+제목.json' 형태로 저장합니다.

json에는 기사내용, 좋아요 순으로 정렬된 댓글, 좋아요 수, 싫어요 수가 저장됩니다.


**쥬피터 노트북 버전에서는 3번 cell 에 원하는 언론사 주소를 입력 하시면 됩니다.**

## 참고

1) 스포츠와 연예 기사는 제외 했음. (구조가 다름)

2) 댓글이 하나도 없는 기사는 제외 했음. <-- 추후에 파마리터로 줄 수 있게

3) json 형태로 저장 했음.

4) 댓글은 320개 까지 수집. 좋아요 순이 가능한 언론사는 좋아요 순서대로 수집.
    한겨레 같은 경우는 좋아요 순이 불가능. 이 경우엔 최신순으로 320개.
    아래 코드를 while True로 수정하면 전부 수집 가능.
    try:
        while i < 30 :
            driver.find_element_by_css_selector(".u_cbox_btn_more").click()
           

## 보완점

한 날짜에 있는 다른 페이지까지 크롤링 하기.

댓글 갯수 파라미터 줄 수 있게 만들기.

언론사 입력 받기.



## 파일 읽는 예시 (encoding 해줘야 함.):

```
    with open('./정치/한겨레_2019.07.28._넉달째맹탕국회…정치가없다.json', encoding = 'utf-8') as f:
        data = json.load(f)
        df = pd.DataFrame({'comment' : data['comment'], 'like':data['like'], 'dont_like':data['dont_like']})
```
