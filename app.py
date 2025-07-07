import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# ✅ 한글 폰트 설정
font_path = "NanumHumanRegular.ttf"
fontprop = fm.FontProperties(fname=font_path)
plt.rcParams["font.family"] = fontprop.get_name()
plt.rcParams["axes.unicode_minus"] = False

# ✅ 기본 설정
DATA_FILE = "monthly_spending.csv"
categories = ["식비", "카페", "쇼핑", "교통", "여가"]

# ✅ 소비 분석 함수
def analyze_spending(spending_data, monthly_budget):
    total_spent = sum(item["amount"] for item in spending_data)
    tips = []

    if total_spent > monthly_budget:
        tips.append(f"⚠️ 예산 초과! 설정한 월 예산({monthly_budget:,}원)을 {total_spent - monthly_budget:,}원 초과했습니다.")
    elif total_spent > monthly_budget * 0.9:
        tips.append("⚠️ 예산의 90% 이상 지출했습니다. 남은 기간 동안 지출을 줄이세요.")
    else:
        tips.append("✅ 예산 내에서 잘 지출하고 있습니다. 좋은 소비 습관입니다!")

    for item in spending_data:
        if item["category"] == "카페" and item["amount"] > 70000:
            tips.append("☕ 카페 소비가 많습니다. 일주일 1~2회로 줄이면 절약에 도움이 됩니다.")
        elif item["category"] == "쇼핑" and item["amount"] > 100000:
            tips.append("🛍️ 쇼핑 지출이 높습니다. 충동구매를 줄이도록 노력해보세요.")
        elif item["category"] == "식비" and item["amount"] > 200000:
            tips.append("🍱 식비가 많은 편입니다. 외식보다는 집밥을 고려해보세요.")
        elif item["category"] == "여가" and item["amount"] > 100000:
            tips.append("🎮 여가 지출이 높습니다. 무료 또는 저비용 활동도 고려해보세요.")
        elif item["category"] == "교통" and item["amount"] > 80000:
            tips.append("🚌 교통비가 높습니다. 정기권 활용을 고려해보세요.")
    return tips

# ✅ 저축 및 습관 조언 함수
def generate_saving_advice(spending_data, monthly_budget):
    total_spent = sum(item["amount"] for item in spending_data)
    remaining = monthly_budget - total_spent
    advices = []

    if remaining > 0:
        advices.append(f"🎯 이번 달 예산의 {remaining:,}원이 남았습니다. 남은 금액은 비상금 계좌나 예적금으로 저축해보는 건 어떨까요?")

    for item in spending_data:
        if item["category"] == "식비" and item["amount"] > 150000:
            advices.append("🍱 식비 지출이 많다면 일주일에 하루는 도시락을 싸거나 집밥 위주로 구성해보세요.")
        elif item["category"] == "카페" and item["amount"] > 70000:
            advices.append("☕ 카페 소비가 많다면 직접 커피 내려 마시기 같은 작은 실천으로도 절약할 수 있어요.")
        elif item["category"] == "여가" and item["amount"] > 80000:
            advices.append("🎮 여가비가 높다면 무료 야외활동, 도서관 이용 등을 고려해보세요.")

    return advices

# ✅ Streamlit UI
st.set_page_config(page_title="소비 분석 자산 조언 시스템", layout="centered")
st.title("💸 소비 분석 자산 조언 시스템")

# ✅ 사이드바
st.sidebar.header("🔧 설정")
selected_month = st.sidebar.selectbox("📆 분석할 월 선택", [f"{i}월" for i in range(1, 13)])
monthly_budget = st.sidebar.slider("💰 월 예산 설정 (원)", 100000, 1000000, 300000, step=50000)
period = st.sidebar.selectbox("📊 비교 기간 선택", ["1개월", "3개월", "6개월", "9개월", "12개월"])

# ✅ 초기화
if st.sidebar.button("🧹 데이터 초기화"):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        st.success("모든 지출 데이터가 초기화되었습니다.")

# ✅ 데이터 불러오기
spending_data = []
df_all = pd.DataFrame()
if os.path.exists(DATA_FILE):
    df_all = pd.read_csv(DATA_FILE)
    df_month = df_all[df_all["month"] == selected_month]
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

st.write(f"### 📆 {selected_month} 예산: {monthly_budget:,}원")

# ✅ 지출 입력
st.subheader("📊 소비 내역 입력")
for item in spending_data:
    item["amount"] = st.number_input(f"{item['category']} 지출 (원)", min_value=0, step=1000, value=item["amount"], key=item["category"])

# ✅ 저장
if st.button("💾 지출 내역 저장"):
    df_new = pd.DataFrame(spending_data)
    df_new["month"] = selected_month

    if not df_all.empty:
        df_all = df_all[df_all["month"] != selected_month]
        df_all = pd.concat([df_all, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_csv(DATA_FILE, index=False)
    st.success(f"{selected_month} 지출 내역이 저장되었습니다!")

# ✅ 총합계
total_amount = sum(item["amount"] for item in spending_data)
st.markdown(f"### 💵 총 지출 합계: {total_amount:,}원")

# ✅ 원형 그래프
st.subheader("📈 지출 비율 시각화")
df = pd.DataFrame(spending_data)
df = df[df["amount"] > 0]
if not df.empty:
    fig, ax = plt.subplots()
    ax.pie(df["amount"], labels=df["category"], autopct="%1.1f%%", startangle=90,
           textprops={'fontproperties': fontprop, 'fontsize': 12})
    ax.axis("equal")
    st.pyplot(fig)
else:
    st.info("지출 내역을 입력하면 그래프가 표시됩니다.")

# ✅ 막대 그래프
if os.path.exists(DATA_FILE):
    st.subheader("📊 월별 지출 막대 그래프")
    period_map = {
        "1개월": 1,
        "3개월": 3,
        "6개월": 6,
        "9개월": 9,
        "12개월": 12
    }
    compare_months = [f"{i}월" for i in range(1, period_map[period] + 1)]
    compare_df = pd.read_csv(DATA_FILE)
    compare_df = compare_df[compare_df["month"].isin(compare_months)]
    pivot_df = compare_df.pivot_table(index="category", columns="month", values="amount", aggfunc="sum", fill_value=0)
    pivot_df = pivot_df.reindex(index=categories)

    fig, ax = plt.subplots(figsize=(10, 5))
    pivot_df.plot(kind="bar", ax=ax, color="orange")  # 생동감 있는 주황
    ax.set_ylabel("지출 금액 (원)", fontproperties=fontprop)
    ax.set_xlabel("카테고리", fontproperties=fontprop)
    ax.set_ylim(0, monthly_budget)
    ax.legend(prop=fontprop)
    plt.xticks(rotation=0, fontproperties=fontprop)
    plt.yticks(fontproperties=fontprop)
    st.pyplot(fig)

# ✅ 소비 조언
st.subheader("💡 소비 조언")
for tip in analyze_spending(spending_data, monthly_budget):
    st.success(tip)

# ✅ 저축 및 습관 조언
for advice in generate_saving_advice(spending_data, monthly_budget):
    st.info(advice)
