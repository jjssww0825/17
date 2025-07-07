import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# ✅ 한글 폰트 설정
font_path = "NanumHumanRegular.ttf"  # GitHub에 함께 업로드해야 함
fontprop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = fontprop.get_name()
plt.rcParams['axes.unicode_minus'] = False

DATA_FILE = "monthly_spending.csv"
categories = ["식비", "카페", "쇼핑", "교통", "여가"]

# ✅ 소비 분석 함수
def analyze_spending(spending_data, monthly_budget):
    total_spent = sum(item['amount'] for item in spending_data)
    tips = []

    if total_spent > monthly_budget:
        tips.append(f"⚠️ 예산 초과! 설정한 월 예산({monthly_budget:,}원)을 {total_spent - monthly_budget:,}원 초과했습니다.")
    elif total_spent > monthly_budget * 0.9:
        tips.append("⚠️ 예산의 90% 이상 지출했습니다. 남은 기간 동안 지출을 줄이세요.")
    else:
        tips.append("✅ 예산 내에서 잘 지출하고 있습니다. 좋은 소비 습관입니다!")

    for item in spending_data:
        if item['category'] == "카페" and item['amount'] > 70000:
            tips.append("☕ 카페 소비가 많습니다. 일주일 1~2회로 줄이면 절약에 도움이 됩니다.")
        elif item['category'] == "쇼핑" and item['amount'] > 100000:
            tips.append("🛍️ 쇼핑 지출이 높습니다. 충동구매를 줄이도록 노력해보세요.")
        elif item['category'] == "식비" and item['amount'] > 200000:
            tips.append("🍱 식비가 많은 편입니다. 외식보다는 집밥을 고려해보세요.")
        elif item['category'] == "여가" and item['amount'] > 100000:
            tips.append("🎮 여가 지출이 높습니다. 무료 또는 저비용 활동도 고려해보세요.")
        elif item['category'] == "교통" and item['amount'] > 80000:
            tips.append("🚌 교통비가 높습니다. 정기권 활용을 고려해보세요.")

    return tips

# ✅ Streamlit 기본 설정
st.set_page_config(page_title="소비 분석 자산 조언 시스템", layout="centered")
st.title("💸 소비 분석 자산 조언 시스템")

# ✅ 설정 사이드바
st.sidebar.header("🔧 설정")
month = st.sidebar.selectbox("📆 분석할 월 선택", [f"{i}월" for i in range(1, 13)])
monthly_budget = st.sidebar.slider("💰 월 예산 설정 (원)", 100000, 1000000, 300000, step=50000)

# ✅ 분석 단위 선택
period = st.sidebar.selectbox("📊 분석 기간 선택", ["1개월", "3개월", "6개월", "9개월", "12개월"])
period_map = {
    "1개월": 1,
    "3개월": 3,
    "6개월": 6,
    "9개월": 9,
    "12개월": 12
}

# ✅ 데이터 초기화
if st.sidebar.button("🧹 데이터 초기화"):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        st.success("모든 지출 데이터가 초기화되었습니다.")

# ✅ 데이터 로드
spending_data = []
df_all = pd.DataFrame()
if os.path.exists(DATA_FILE):
    df_all = pd.read_csv(DATA_FILE)
    df_month = df_all[df_all["month"] == month]
    if not df_month.empty:
        for cat in categories:
            amount = df_month[df_month["category"] == cat]["amount"]
            if not amount.empty:
                spending_data.append({"category": cat, "amount": int(amount.values[0])})
            else:
                spending_data.append({"category": cat, "amount": 0})
    else:
        spending_data = [{"category": cat, "amount": 0} for cat in categories]
else:
    spending_data = [{"category": cat, "amount": 0} for cat in categories]

st.write(f"### 📆 {month} 예산: {monthly_budget:,}원")

# ✅ 지출 입력
st.subheader("📊 소비 내역 입력")
for item in spending_data:
    item["amount"] = st.number_input(
        f"{item['category']} 지출 (원)", min_value=0, step=1000, value=item["amount"], key=item["category"]
    )

# ✅ 지출 저장
if st.button("💾 지출 내역 저장"):
    df_new = pd.DataFrame(spending_data)
    df_new["month"] = month

    if not df_all.empty:
        df_all = df_all[df_all["month"] != month]
        df_all = pd.concat([df_all, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_csv(DATA_FILE, index=False)
    st.success(f"{month} 지출 내역이 저장되었습니다!")

# ✅ 총 지출 합계
total_amount = sum(item["amount"] for item in spending_data)
st.markdown(f"### 💵 총 지출 합계: {total_amount:,}원")

# ✅ 원형 그래프
st.subheader("📈 지출 비율 시각화")
df = pd.DataFrame(spending_data)
df = df[df['amount'] > 0]

if not df.empty:
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        df["amount"],
        labels=df["category"],
        autopct="%1.1f%%",
        startangle=90,
        textprops={'fontproperties': fontprop, 'fontsize': 12}
    )
    for text in texts + autotexts:
        text.set_fontproperties(fontprop)
    ax.axis("equal")
    st.pyplot(fig)
else:
    st.info("지출 내역을 입력하면 그래프가 표시됩니다.")

# ✅ 월별 비교 막대 그래프
if os.path.exists(DATA_FILE):
    st.subheader("📊 월별 지출 막대 그래프")
    compare_df = pd.read_csv(DATA_FILE)

    # 최근 선택한 월 기준으로 period 개월 만큼 선택
    current_month = int(month.replace("월", ""))
    months_to_include = [f"{i}월" for i in range(current_month - period_map[period] + 1, current_month + 1) if i >= 1]
    filtered_df = compare_df[compare_df["month"].isin(months_to_include)]
    pivot_df = filtered_df.pivot_table(index="category", columns="month", values="amount", aggfunc="sum", fill_value=0)

    fig, ax = plt.subplots(figsize=(10, 5))
    pivot_df.plot(kind="bar", ax=ax)
    ax.set_ylabel("지출 금액 (원)", fontproperties=fontprop)
    ax.set_xlabel("카테고리", fontproperties=fontprop)
    ax.legend(title="월", prop=fontprop)
    plt.xticks(rotation=0, fontproperties=fontprop)
    plt.yticks(fontproperties=fontprop)
    st.pyplot(fig)

# ✅ 소비 조언 (맨 아래)
st.subheader("💡 소비 조언")
tips = analyze_spending(spending_data, monthly_budget)
for tip in tips:
    st.success(tip)
