import requests
import datetime
import pandas as pd
from pykrx import stock
import google.generativeai as genai
import os

# 괄호 안에는 실제 값이 아니라 설정한 '이름'이 들어가야 합니다.
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

def main():
    target_date = datetime.datetime.now().strftime("%Y%m%d")
    
    try:
        # 데이터 수집
        df_kse = stock.get_market_cap_by_ticker(target_date, market="KOSPI")
        df_ksd = stock.get_market_cap_by_ticker(target_date, market="KOSDAQ")
        
        combined = pd.concat([df_kse, df_ksd])
        if combined.empty:
            print("데이터가 아직 생성되지 않았습니다.")
            return

        top_30 = combined.sort_values(by="거래대금", ascending=False).head(30)
        stock_names = [stock.get_market_ticker_name(ticker) for ticker in top_30.index]

        # AI 분석
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"다음 한국 주식 종목들을 현재 시장 테마별로 분류하고 요약해줘: {', '.join(stock_names)}"
        response = model.generate_content(prompt)

        # 텔레그램 전송
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": response.text})
        print("✅ 분석 결과 전송 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
