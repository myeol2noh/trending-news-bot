import os
from anthropic import Anthropic
from datetime import datetime
import pytz

class IssueGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
        
        # 아이콘 리스트
        self.icons = ['🔥', '⚡', '💥', '🚨', '📢', '🎯', '💡', '🌟', '🔔', '💫']
    
    def generate_issue_list(self, news_items, time_slot):
        """이슈 리스트 생성 (10개, 35자 이내)"""
        if not news_items or len(news_items) < 10:
            return None
        
        # 뉴스 제목들을 요약
        news_titles = ""
        for i, news in enumerate(news_items, 1):
            news_titles += f"{i}. {news['title']}\n"
        
        time_context = {
            "07:00": "아침에 체크할 주요 이슈들",
            "12:00": "점심시간에 알아둘 핫한 소식들", 
            "18:00": "퇴근길에 확인할 오늘의 이슈들"
        }
        
        context = time_context.get(time_slot, "주요 이슈들")
        
        prompt = f"""
다음 네이버 뉴스들을 바탕으로 {context}를 20대 여성 반말체로 정리해줘.

=== 네이버 뉴스 제목들 ===
{news_titles}

조건:
- 정확히 10개 항목
- 각 항목은 35자 이내 (공백 포함)
- 20대 여성 반말체 (친근하고 캐주얼하게)
- 아이콘은 사용하지 말고 번호만 사용
- 형식: 1. [35자 이내 요약]
- 텔레그램에서 복사해서 스레드에 바로 붙여넣을 수 있게 본문만
- 다른 부연설명이나 인사말 없이 리스트만

예시 형식:
1. 윤대통령 탄핵안 가결, 헌재 심판 시작돼
2. 비트코인 10만달러 돌파, 가상화폐 열풍
3. ...

시간: {time_slot}
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=400,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            
            # 아이콘 추가
            lines = content.split('\n')
            result_lines = []
            
            for i, line in enumerate(lines):
                if line.strip() and i < 10:
                    # 번호 부분을 아이콘으로 교체
                    if line.strip().startswith(f"{i+1}."):
                        icon = self.icons[i] if i < len(self.icons) else '📌'
                        new_line = line.replace(f"{i+1}.", f"{icon}")
                        result_lines.append(new_line)
            
            return '\n'.join(result_lines)
            
        except Exception as e:
            print(f"이슈 리스트 생성 오류: {e}")
            return None
    
    def generate_hot_issue(self, news_items):
        """오늘의 핫이슈 생성 (300자 이내)"""
        if not news_items:
            return None
        
        # 가장 인기 있는 뉴스 1개 선택
        top_news = news_items[0]
        
        prompt = f"""
다음 뉴스를 바탕으로 오늘의 가장 핫한 이슈를 20대 여성 반말체로 300자 이내로 정리해줘.

=== 오늘의 탑 뉴스 ===
제목: {top_news['title']}

조건:
- 300자 이내 (공백 포함)
- 20대 여성 반말체 (친근하고 자연스럽게)
- 왜 이 이슈가 핫한지, 배경과 현재 상황 포함
- 텔레그램에서 복사해서 스레드에 바로 붙여넣을 수 있게 본문만
- 다른 부연설명이나 제목 없이 내용만
- 아이콘이나 이모지 사용하지 말것

예시 톤:
윤석열 대통령 탄핵소추안이 국회를 통과했어. 계엄령 선포 후폭풍이 이렇게까지 클 줄 몰랐는데... 헌법재판소에서 최종 결정이 나올 때까지 직무가 정지되고, 한덕수 총리가 권한대행을 맡게 됐대. 정치권은 완전 뒤바뀔 분위기고, 경제에도 영향이 클 것 같아서 걱정이야.
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=400,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"핫이슈 생성 오류: {e}")
            return None

if __name__ == "__main__":
    # 테스트용
    generator = IssueGenerator()
    test_news = [
        {'title': '윤석열 대통령 탄핵소추안 국회 통과', 'link': 'http://test.com'},
        {'title': '비트코인 사상 첫 10만달러 돌파', 'link': 'http://test.com'},
    ]
    
    # 이슈 리스트 테스트
    issues = generator.generate_issue_list(test_news * 5, '07:00')  # 10개 만들기
    if issues:
        print("=== 이슈 리스트 ===")
        print(issues)
    
    # 핫이슈 테스트
    hot_issue = generator.generate_hot_issue([test_news[0]])
    if hot_issue:
        print("\n=== 오늘의 핫이슈 ===")
        print(hot_issue)
