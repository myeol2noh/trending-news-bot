import os
import time
from anthropic import Anthropic
from datetime import datetime
import pytz

class IssueGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
        
        # 아이콘 리스트
        self.icons = ['🔥', '⚡', '💥', '🚨', '📢', '🎯', '💡', '🌟', '🔔', '💫']
    
    def generate_issue_list(self, news_items, time_slot):
        """이슈 리스트 생성 (10개, 35자 이내) - 디버깅 추가"""
        print(f"🔍 generate_issue_list 시작 - 뉴스 개수: {len(news_items)}")
        
        if not news_items or len(news_items) < 8:
            print(f"❌ 뉴스 개수 부족: {len(news_items)}개")
            return None
        
        # 뉴스 제목을 더 간단하게 정리 (8개만, 제목 단축)
        news_titles = ""
        for i, news in enumerate(news_items[:8], 1):
            title = news['title'][:60]  # 60자로 제한
            news_titles += f"{i}. {title}\n"
            print(f"  뉴스 {i}: {title}")
        
        # 매우 간단한 프롬프트
        prompt = f"""다음 뉴스를 20대 여성 반말로 10개 요약해줘. 각 35자 이내.

{news_titles}

형식: 1. 내용요약
시간: {time_slot}"""

        print(f"📝 프롬프트 길이: {len(prompt)}자")
        print(f"📝 프롬프트 내용: {prompt[:200]}...")

        # 재시도 로직
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"AI 요청 시도 {attempt + 1}/{max_retries}")
                
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=250,  # 더 줄임
                    temperature=0.2,  # 더 안정적으로
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.content[0].text.strip()
                print(f"✅ AI 응답 받음 - 길이: {len(content)}자")
                print(f"📄 AI 응답 내용: {content}")
                
                # 번호 그대로 유지 (아이콘 교체 안 함)
                lines = content.split('\n')
                print(f"🔍 응답을 {len(lines)}개 줄로 분리")
                
                result_lines = []
                
                for line in lines:
                    line_clean = line.strip()
                    print(f"  줄: '{line_clean}'")
                    
                    if line_clean:  # 빈 줄 건너뛰기
                        # 숫자로 시작하는 줄 찾기 (1., 2., 3. 등)
                        import re
                        if re.match(r'^\d+\.', line_clean):
                            result_lines.append(line_clean)  # 번호 그대로 사용
                            print(f"    → 추가: '{line_clean}'")
                            
                            if len(result_lines) >= 10:  # 최대 10개
                                break
                        else:
                            print(f"    → 숫자 패턴 없음: '{line_clean[:20]}'")
                
                result = '\n'.join(result_lines)
                print(f"🎯 최종 결과 길이: {len(result)}자")
                print(f"🎯 최종 결과: {result}")
                print(f"✅ AI 요청 성공 (시도 {attempt + 1})")
                
                if not result.strip():
                    print("❌ 빈 결과 반환")
                    return None
                
                return result
                
            except Exception as e:
                print(f"❌ AI 요청 실패 (시도 {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    print("모든 재시도 실패")
                    return None
                print(f"⏳ {2 * (attempt + 1)}초 후 재시도...")
                time.sleep(2 * (attempt + 1))  # 지수적 백오프
    
    def generate_hot_issue(self, news_items):
        """오늘의 핫이슈 생성 (300자 이내) - 디버깅 추가"""
        print(f"🔍 generate_hot_issue 시작 - 뉴스 개수: {len(news_items)}")
        
        if not news_items:
            print("❌ 뉴스 없음")
            return None
        
        # 가장 인기 있는 뉴스 1개 선택
        top_news = news_items[0]
        title = top_news['title'][:80]  # 제목 80자로 제한
        print(f"📰 선택된 뉴스: {title}")
        
        # 매우 간단한 프롬프트
        prompt = f"""이 뉴스를 20대 여성 반말로 300자 이내 요약:

제목: {title}

조건: 친근한 반말, 배경설명 포함"""

        print(f"📝 핫이슈 프롬프트 길이: {len(prompt)}자")

        # 재시도 로직
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"핫이슈 AI 요청 시도 {attempt + 1}/{max_retries}")
                
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=200,  # 더 줄임
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                result = response.content[0].text.strip()
                print(f"✅ 핫이슈 AI 응답 받음 - 길이: {len(result)}자")
                print(f"📄 핫이슈 내용: {result}")
                print(f"✅ 핫이슈 AI 요청 성공 (시도 {attempt + 1})")
                
                if not result.strip():
                    print("❌ 빈 핫이슈 결과 반환")
                    return None
                
                return result
                
            except Exception as e:
                print(f"❌ 핫이슈 AI 요청 실패 (시도 {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    print("핫이슈 모든 재시도 실패")
                    return None
                print(f"⏳ {2 * (attempt + 1)}초 후 재시도...")
                time.sleep(2 * (attempt + 1))

# 테스트용
if __name__ == "__main__":
    generator = IssueGenerator()
    test_news = [
        {'title': '윤석열 대통령 탄핵소추안 국회 통과', 'link': 'http://test.com'},
        {'title': '비트코인 사상 첫 10만달러 돌파', 'link': 'http://test.com'},
        {'title': '삼성전자 3분기 실적 부진 발표', 'link': 'http://test.com'},
        {'title': '북한 ICBM 발사, 한미일 공동 대응', 'link': 'http://test.com'},
        {'title': '네이버 AI 신기술 공개', 'link': 'http://test.com'},
        {'title': '한국 월드컵 16강 진출', 'link': 'http://test.com'},
        {'title': '전기요금 또 인상 예정', 'link': 'http://test.com'},
        {'title': 'BTS 지민 솔로 앨범 발표', 'link': 'http://test.com'},
    ]
    
    print("=== 이슈 리스트 테스트 ===")
    issues = generator.generate_issue_list(test_news, '07:00')
    if issues:
        print("최종 이슈 리스트:")
        print(issues)
    else:
        print("이슈 리스트 생성 실패")
    
    print("\n=== 핫이슈 테스트 ===")
    hot_issue = generator.generate_hot_issue([test_news[0]])
    if hot_issue:
        print("최종 핫이슈:")
        print(hot_issue)
    else:
        print("핫이슈 생성 실패")
