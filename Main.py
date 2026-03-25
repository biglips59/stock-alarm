import requests
import datetime
import pandas as pd
from pykrx import stock
import google.generativeai as genai
import os

# 보안을 위해 설정값들은 외부(Secrets)에서 가져옵니다
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

def main():
    # 실행 시점의 날짜 (9:30 실행 시 당일 데이터 수집)
    target_date = datetime.datetime.now().strftime("%Y%m%d")
    
    try:
        # 1. 거래대금 상위 종목 수집
        df_kse = stock.get_market_cap_by_ticker(target_date, market="KOSPI")
        df_ksd = stock.get_market_cap_by_ticker(target_date, market="KOSDAQ")
        
        combined = pd.concat([df_kse, df_ksd])
        if combined.empty:
            print("데이터가 아직 생성되지 않았습니다.")
            return

        # 거래대금 기준 상위 30개 종목명 추출
        top_30 = combined.sort_values(by="거래대금", ascending=False).head(30)
        stock_names = [stock.get_market_ticker_name(ticker) for ticker in top_30.index]

        # 2. Gemini AI 테마 분석
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"다음 한국 주식 종목들을 현재 시장 테마별로 분류하고 요약해줘: {', '.join(stock_names)}"
        response = model.generate_content(prompt)

        # 3. 텔레그램 메시지 전송
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": response.text})
        print("✅ 분석 결과 전송 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
