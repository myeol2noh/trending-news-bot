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
    
    def validate_thread(self, content):
        """쓰레드 품질 검증"""
        if not content:
            return False, "내용이 없습니다"
        
        # 길이 체크
        if len(content) < 50:
            return False, "너무 짧습니다 (50자 미만)"
        if len(content) > 250:
            return False, "너무 깁니다 (250자 초과)"
        
        # 기본 요소 체크
        has_emoji = any(ord(char) > 127 for char in content if not char.isalnum())
        has_number = any(char.isdigit() for char in content)
        
        if not has_emoji:
            return False, "이모지가 없습니다"
        if not has_number:
            return False, "구체적인 숫자가 없습니다"
        
        return True, "검증 통과"

# 테스트용
if __name__ == "__main__":
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
        
        # 품질 검증
        is_valid, message = generator.validate_thread(thread['content'])
        print(f"검증 결과: {message}")
