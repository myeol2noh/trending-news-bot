import requests
import feedparser
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pytz
import re

class TrendingNewsCrawler:
    def __init__(self):
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_current_schedule(self):
        """현재 시간에 맞는 스케줄 반환 (7시 추가)"""
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst)
        current_hour = now.strftime('%H:00')
        
        schedules = ['07:00', '09:00', '12:00', '15:00', '18:00', '21:00']
        if current_hour not in schedules:
            hour = int(now.strftime('%H'))
            for schedule in schedules:
                schedule_hour = int(schedule.split(':')[0])
                if hour <= schedule_hour:
                    current_hour = schedule
                    break
            else:
                current_hour = '21:00'
        
        return current_hour
    
    def crawl_google_news_trending(self, rss_url, limit=5):
        """구글 뉴스 인기 기사 크롤링"""
        try:
            feed = feedparser.parse(rss_url)
            news_items = []
            
            for entry in feed.entries[:limit]:
                # 제목에서 불필요한 정보 제거
                title = entry.title
                title = re.sub(r'\s*-\s*[^-]*

### src/thread_generator.py (인기 뉴스용)
```python
import os
from anthropic import Anthropic
from datetime import datetime
import pytz

class ThreadGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
    
    def generate_thread_from_news(self, news_items, category, time_slot):
        """인기 뉴스 기반 쓰레드 생성"""
        if not news_items:
            return None
        
        # 인기 뉴스 요약을 위한 프롬프트 구성
        news_summary = ""
        for i, news in enumerate(news_items[:3], 1):  # 상위 3개만 사용
            popularity = news.get('popularity_score', 0)
            news_summary += f"{i}. {news['title']}\n"
            if news['summary']:
                news_summary += f"   요약: {news['summary'][:100]}...\n"
            news_summary += f"   출처: {news.get('source', 'Unknown')}\n"
            news_summary += f"   인기도: {popularity}\n\n"
        
        # 시간대별 맞춤 프롬프트
        time_context = {
            "07:00": "아침 출근 준비하는 사람들을 위한 간결한 뉴스 브리핑",
            "09:00": "출근길에서 읽기 좋은 핵심 뉴스",
            "12:00": "점심시간 휴식 중 확인하는 주요 이슈",
            "15:00": "오후 업무 중 알아둘 만한 소식",
            "18:00": "퇴근길에서 챙겨볼 중요 뉴스",
            "21:00": "하루 마무리하며 정리하는 주요 소식"
        }
        
        context = time_context.get(time_slot, "주요 뉴스 정리")
        
        prompt = f"""
다음은 현재 가장 인기 있는 뉴스들입니다. 이를 바탕으로 {context} 스타일의 쓰레드를 한국어로 작성해주세요.

=== 인기 뉴스 TOP 3 ===
{news_summary}

조건:
- 200자 이내 (공백 포함)
- 가장 화제가 되는 뉴스 1-2개 선별해서 핵심만
- 왜 지금 인기/화제인지 이유 포함
- 구체적인 숫자나 사실 활용
- 3-4개 짧고 임팩트 있는 문장
- 뉴스픽 스타일: 간결하고 팩트 중심, 트렌드 감각
- 이모지 1-2개만 사용

형식 예시:
🔥 [가장 화제가 되는 뉴스 팩트]
💡 [왜 지금 인기인지/중요한지 분석]  
⚡ [관련 트렌드나 향후 전망]

시간대: {time_slot} ({context})
현재 시각: {datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M')}
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                temperature=0.6,  # 약간의 창의성 허용
                messages=[{"role": "user", "content": prompt}]
            )
            
            thread_content = response.content[0].text.strip()
            
            return {
                "time_slot": time_slot,
                "category": category,
                "content": thread_content,
                "source_news": news_items[:3],
                "generated_at": datetime.now(pytz.timezone('Asia/Seoul')).isoformat(),
                "char_count": len(thread_content),
                "trending_context": context
            }
            
        except Exception as e:
            print(f"쓰레드 생성 오류: {e}")
            return None

if __name__ == "__main__":
    # 테스트용
    generator = ThreadGenerator()
    test_news = [
        {
            "title": "삼성전자 3분기 실적 발표, 반도체 회복세",
            "summary": "메모리 반도체 가격 상승으로 영업이익 증가",
            "source": "네이버 뉴스",
            "popularity_score": 1250
        },
        {
            "title": "테슬라 자율주행 업데이트 논란",
            "summary": "FSD 베타 버전에서 안전성 문제 제기",
            "source": "Reddit",
            "popularity_score": 890
        }
    ]
    
    thread = generator.generate_thread_from_news(test_news, "인기 뉴스", "09:00")
    if thread:
        print("=== 생성된 쓰레드 ===")
        print(f"내용: {thread['content']}")
        print(f"글자수: {thread['char_count']}자")
