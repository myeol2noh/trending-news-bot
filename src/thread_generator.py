### src/thread_generator.py  
```python
import os
from anthropic import Anthropic
from datetime import datetime
import pytz

class ThreadGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
    
    def generate_thread_from_news(self, news_items, category, time_slot):
        """뉴스 기반 쓰레드 생성"""
        if not news_items:
            return None
        
        # 뉴스 요약을 위한 프롬프트 구성
        news_summary = ""
        for i, news in enumerate(news_items[:3], 1):  # 상위 3개만 사용
            news_summary += f"{i}. {news['title']}\n"
            if news['summary']:
                news_summary += f"   요약: {news['summary'][:100]}...\n"
            news_summary += f"   출처: {news.get('source', 'Unknown')}\n\n"
        
        prompt = f"""
다음 {category} 관련 최신 뉴스들을 바탕으로 뉴스픽 스타일의 쓰레드를 한국어로 작성해줘.

=== 최신 뉴스 ===
{news_summary}

조건:
- 200자 이내 (공백 포함)
- 가장 임팩트 있는 뉴스 1-2개 선별
- 구체적인 숫자나 사실 포함
- 3-4개 짧은 문장으로 구성
- 뉴스픽 스타일: 간결하고 팩트 중심
- 이모지 1-2개만 사용

형식 예시:
📰 [핵심 뉴스 팩트]
💡 [왜 중요한지 인사이트]  
🔍 [업계 임팩트나 전망]

시간대: {time_slot} ({category})
현재 시각: {datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M')}
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )
            
            thread_content = response.content[0].text.strip()
            
            return {
                "time_slot": time_slot,
                "category": category,
                "content": thread_content,
                "source_news": news_items[:3],
                "generated_at": datetime.now(pytz.timezone('Asia/Seoul')).isoformat(),
                "char_count": len(thread_content)
            }
            
        except Exception as e:
            print(f"쓰레드 생성 오류: {e}")
            return None

if __name__ == "__main__":
    # 테스트용
    generator = ThreadGenerator()
    test_news = [
        {
            "title": "OpenAI GPT-4 업데이트 발표",
            "summary": "새로운 기능 추가로 성능 향상",
            "source": "TechCrunch"
        }
    ]
    
    thread = generator.generate_thread_from_news(test_news, "AI/스타트업", "09:00")
    if thread:
        print(thread['content'])
