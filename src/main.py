#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from datetime import datetime
import pytz

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news_crawler import NewsCrawler
from thread_generator import ThreadGenerator
from discord_webhook import send_to_discord

def main():
    """메인 실행: 뉴스 크롤링 → AI 요약 → Discord 전송"""
    print("=== 자동 뉴스 쓰레드 봇 시작 ===")
    
    # 환경 변수 확인
    required_env = ['CLAUDE_API_KEY', 'DISCORD_WEBHOOK_URL']
    missing_env = [env for env in required_env if not os.getenv(env)]
    
    if missing_env:
        print(f"❌ 필수 환경 변수 누락: {missing_env}")
        sys.exit(1)
    
    # 1. 인기 뉴스 크롤링
    print("🔥 인기 뉴스 수집 중...")
    from trending_crawler import TrendingNewsCrawler
    crawler = TrendingNewsCrawler()
    current_schedule = crawler.get_current_schedule()
    trending_news = crawler.get_trending_news(current_schedule)
    
    if not trending_news:
        print("❌ 수집된 인기 뉴스가 없습니다.")
        sys.exit(1)
    
    print(f"✅ {len(trending_news)}개 인기 뉴스 수집 완료")
    for i, news in enumerate(trending_news, 1):
        popularity = news.get('popularity_score', 0)
        print(f"  {i}. {news['title']} (인기도: {popularity})")
    
    # 2. AI 쓰레드 생성
    print("\n🤖 인기 뉴스 쓰레드 생성 중...")
    generator = ThreadGenerator()
    
    # 스케줄 설정에서 카테고리 가져오기
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    category = config['news_sources'][current_schedule]['category']
    thread_data = generator.generate_thread_from_news(trending_news, category, current_schedule)
    
    if not thread_data:
        print("❌ 쓰레드 생성 실패")
        sys.exit(1)
    
    # 3. 생성 결과 출력
    print("\n=== 생성된 인기 뉴스 쓰레드 ===")
    print(f"시간대: {thread_data['time_slot']}")
    print(f"카테고리: {thread_data['category']}")
    print(f"글자수: {thread_data['char_count']}자")
    print(f"\n📱 쓰레드 내용:")
    print(thread_data['content'])
    
    print(f"\n🔥 참고 인기 뉴스:")
    for i, news in enumerate(thread_data['source_news'], 1):
        popularity = news.get('popularity_score', 0)
        print(f"{i}. {news['title']} (인기도: {popularity})")
        print(f"   🔗 {news['link']}")
        print(f"   📰 출처: {news['source']}")
    
    # 4. Discord로 전송
    print("\n📤 Discord 전송 중...")
    
    # Discord용 메시지 구성 (인기 뉴스용)
    discord_thread = {
        'time_slot': thread_data['time_slot'],
        'category': thread_data['category'], 
        'keyword': '인기 뉴스',
        'content': thread_data['content'],
        'generated_at': thread_data['generated_at'],
        'source_news': thread_data['source_news'],
        'trending_info': f"상위 {len(trending_news)}개 인기 뉴스 기반"
    }
    
    success = send_to_discord(discord_thread)
    
    if success:
        print("✅ Discord 전송 성공!")
        
        # 로그 저장
        save_thread_log(thread_data)
        print("✅ 로그 저장 완료!")
        
    else:
        print("❌ Discord 전송 실패")
        sys.exit(1)

def save_thread_log(thread_data):
    """쓰레드 로그 저장"""
    log_file = f"logs/trending_thread_log_{datetime.now().strftime('%Y%m%d')}.json"
    os.makedirs('logs', exist_ok=True)
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except:
        logs = []
    
    logs.append(thread_data)
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
