import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# ✅ 한글 폰트 설정
font_path = "NanumGothic-Bold.ttf"
fontprop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = fontprop.get_name()
plt.rcParams['axes.unicode_minus'] = False

# ✅ 소비 조언 함수
def analyze_spending(spending_data, monthly_budget):
    total_spent = sum(item['amount'] for item in spending_data)
    tips = []

    if total_spent > monthly_budget:
        tips.append(f"예산 초과! 설정한 예산({monthly_budget:,}원)을 {total_spent - monthly_budget:,}원 초과했습니다.")
    elif total_spent > monthly_budget * 0.9:
        tips.append("예산의 90% 이상을 지출했습니다.")
    elif total_spent < monthly_budget * 0.5:
        tips.append("예산의 절반 이하만 지출 중입니다. 과도한 절약은 스트레스를 유발할 수 있어요.")
    else:
        tips.append("예산 내에서 잘 지출하고 있습니다.")

    for item in spending_data:
        c, a = item['category'], item['amount']
        if c == "카페" and a > 70000:
            tips.append("☕ 카페 지출이 높습니다. 줄이는 걸 고려해보세요.")
        elif c == "쇼핑" and a > 100000:
            tips.append("🛍️ 쇼핑 지출이 많습니다. 충동구매를 주의하세요.")
        elif c == "식비" and a > 200000:
            tips.append("🍚 식비가 많습니다. 외식을 줄이고 집밥을 늘려보세요.")
        elif c == "여가" and a > 100000:
            tips.append("🎮 여가비 지출이 높습니다. 저비용 활동도 고려해보세요.")
        elif c == "기타" and a > 150000:
            tips.append("기타 지출이 과도할 수 있습니다. 꼭 필요한 소비인지 점검해보세요.")

    saving_score = max(0, min(100, int((1 - total_spent / monthly_budget) * 100)))
    tips.append(f"📊 절약 점수: {saving_score}/100")
    recommended_saving = int(monthly_budget * 0.2)
    tips.append(f"💡 최소 저축 권장액: {recommended_saving:,}원")
    return tips

# ✅ Streamlit 앱
st.title("💰 월간 소비 분석 자산 조언 시스템")

# 사이드바 입력
st.sidebar.header("🔧 설정")
month = st.sidebar.selectbox("분석할 월", [f"{i}월" for i in range(1, 13)])
budget = st.sidebar.slider("월 예산 설정 (원)", 100000, 1000000, 300000, 50000)

st.write(f"### 📅 {month} 예산: {budget:,}원")

categories = ["식비", "카페", "쇼핑", "교통", "여가", "기타"]
spending_data = []

st.subheader("📝 소비 항목 입력")
for c in categories:
    amt = st.number_input(f"{c} 지출 (원)", min_value=0, step=1000, key=c)
    spending_data.append({"month": month, "category": c, "amount": amt})

if st.button("저장 및 분석"):
    df_new = pd.DataFrame(spending_data)
    if 'monthly_spending.csv' in os.listdir():
        df_old = pd.read_csv('monthly_spending.csv')
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new
    df_all.to_csv('monthly_spending.csv', index=False)
    st.success("소비 데이터 저장 완료!")

    # 🔍 월별 비교 시각화
    st.subheader("📊 월별 소비 비교")
    pivot = df_all.pivot_table(index="category", columns="month", values="amount", aggfunc="sum", fill_value=0)
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    pivot.plot(kind="bar", ax=ax2, fontsize=10)
    plt.xticks(rotation=45, fontproperties=fontprop)
    plt.legend(prop=fontprop)
    st.pyplot(fig2)

# 원형 차트
st.subheader("📈 소비 비율 시각화")
if sum([item['amount'] for item in spending_data]) > 0:
    df = pd.DataFrame(spending_data)
    df = df[df['amount'] > 0]
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        df['amount'],
        labels=df['category'],
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontproperties': fontprop}
    )
    for t in texts + autotexts:
        t.set_fontproperties(fontprop)
    ax.axis('equal')
    st.pyplot(fig)

# 소비 조언
st.subheader("💡 소비 조언")
for t in analyze_spending(spending_data, budget):
    st.success(t)
