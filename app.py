import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

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
        category, amount = item["category"], item["amount"]
        if category == "카페" and amount > 70000:
            tips.append("☕ 카페 소비가 많습니다. 일주일 1~2회로 줄이면 절약에 도움이 됩니다.")
        if category == "쇼핑" and amount > 100000:
            tips.append("🛍️ 쇼핑 지출이 높습니다. 충동구매를 줄이도록 노력해보세요.")
        if category == "식비" and amount > 200000:
            tips.append("🍱 식비가 많은 편입니다. 외식보다는 집밥을 고려해보세요.")
        if category == "여가" and amount > 100000:
            tips.append("🎮 여가 지출이 높습니다. 무료 또는 저비용 활동도 고려해보세요.")
        if category == "교통" and amount > 80000:
            tips.append("🚌 교통비가 높습니다. 정기권 활용을 고려해보세요.")
    
    return tips[:3]  # 최대 3개만 출력

# ✅ 저축 및 습관 조언 함수
def saving_and_habit_tips(spending_data, monthly_budget):
    total_spent = sum(item["amount"] for item in spending_data)
    left = monthly_budget - total_spent
    saving_tips = []

    if left > 0:
        saving_tips.append(f"🎯 이번 달 예산의 {left:,}원이 남았습니다. 비상금 계좌나 예적금으로 저축해보는 건 어떨까요?")

    for item in spending_data:
        if item["category"] == "식비" and item["amount"] > 180000:
            saving_tips.append("🍱 일주일에 하루는 도시락을 싸거나 집밥 위주로 구성해보세요.")
        if item["category"] == "카페" and item["amount"] > 35000:
            saving_tips.append("☕ 직접 커피 내려 마시기 같은 작은 실천으로 절약할 수 있어요.")
        if item["category"] == "여가" and item["amount"] > 52000:
            saving_tips.append("🎮 무료 야외활동이나 도서관 이용도 좋은 대안이 될 수 있어요.")
    
    return saving_tips[:2]

# ✅ 이상치 감지 함수
def detect_outliers(spending_data):
    category_avg = {
        "식비": 180000, "카페": 35000, "쇼핑": 20000, "교통": 10000, "여가": 52000
    }
    alerts = []
    for item in spending_data:
        cat = item["category"]
        amt = item["amount"]
        if cat in category_avg and amt > category_avg[cat] * 1.5:
            alerts.append(f"🚨 {cat} 지출이 평소보다 150% 이상 증가했어요!")
    return alerts

# ✅ 시간 기반 변화 탐지 함수
def detect_trends(df_all, category, current_month_index):
    if current_month_index < 3:
        return None
    trend_df = df_all[df_all["category"] == category]
    trend_df = trend_df.sort_values(by="month_num")
    recent = trend_df.tail(3)["amount"].values
    if len(recent) == 3 and recent[0] < recent[1] < recent[2]:
        return f"📈 최근 3개월간 {category} 지출이 꾸준히 증가하고 있어요."
    return None

# ✅ 소비자 유형 분류
def classify_user(spending_data):
    total = sum(item["amount"] for item in spending_data)
    fixed = next((item["amount"] for item in spending_data if item["category"] == "교통"), 0)
    ratio = fixed / total if total > 0 else 0
    if ratio >= 0.4:
        return "💡 당신은 '계획형 소비자' 유형입니다. 장기 예산 계획을 수립해보세요."
    else:
        return "⚠️ 당신은 '즉흥적 지출' 경향이 있습니다. 주간 지출 목표를 설정해보세요!"

# ✅ 클러스터링 유사 그룹 조언
def cluster_feedback(spending_data):
    leisure = next((item["amount"] for item in spending_data if item["category"] == "여가"), 0)
    if leisure > 70000:
        return "🔍 당신은 ‘여가 중심 소비자’입니다. 이번 달은 무료 공연, 공공 체육시설을 활용해보는 건 어때요?"
    return "🧳 비슷한 소비자들은 계절마다 예산을 재설정하고 있어요. 지출 달력을 만들어보세요."

# ✅ Streamlit UI
st.set_page_config("소비 분석 자산 조언 시스템", layout="centered")
st.title("💸 소비 분석 자산 조언 시스템")

# 사이드바
st.sidebar.header("📋 설정")
selected_month = st.sidebar.selectbox("월 선택", [f"{i}월" for i in range(1, 13)])
monthly_budget = st.sidebar.slider("예산 (원)", 100000, 1000000, 300000, step=50000)

# 파일 초기화
if st.sidebar.button("🧹 데이터 초기화"):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        st.success("지출 데이터 초기화 완료")

# ✅ 데이터 불러오기
spending_data = []
df_all = pd.DataFrame()
if os.path.exists(DATA_FILE):
    df_all = pd.read_csv(DATA_FILE)
    df_month = df_all[df_all["month"] == selected_month]
    for cat in categories:
        amt = df_month[df_month["category"] == cat]["amount"]
        spending_data.append({"category": cat, "amount": int(amt.values[0]) if not amt.empty else 0})
else:
    spending_data = [{"category": cat, "amount": 0} for cat in categories]

st.write(f"### 📆 {selected_month} 예산: {monthly_budget:,}원")

# ✅ 지출 입력
st.subheader("📊 소비 내역 입력")
for item in spending_data:
    item["amount"] = st.number_input(f"{item['category']} 지출 (원)", min_value=0, value=item["amount"], key=item["category"])

# ✅ 저장
if st.button("💾 저장"):
    df_new = pd.DataFrame(spending_data)
    df_new["month"] = selected_month
    df_new["month_num"] = int(selected_month.replace("월", ""))
    df_all = df_all[df_all["month"] != selected_month] if not df_all.empty else pd.DataFrame()
    df_all = pd.concat([df_all, df_new], ignore_index=True)
    df_all.to_csv(DATA_FILE, index=False)
    st.success("저장 완료")

# ✅ 시각화
df = pd.DataFrame(spending_data)
df = df[df["amount"] > 0]
if not df.empty:
    st.subheader("📈 지출 비율")
    fig1, ax1 = plt.subplots()
    ax1.pie(df["amount"], labels=df["category"], autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)

# ✅ 소비 조언
st.subheader("💡 소비 조언")
for tip in analyze_spending(spending_data, monthly_budget):
    st.success(tip)

# ✅ 저축 및 습관 조언
st.subheader("💾 저축/습관 조언")
for tip in saving_and_habit_tips(spending_data, monthly_budget):
    st.info(tip)

# ✅ 이상치 감지
st.subheader("🚨 지출 이상 탐지")
for warning in detect_outliers(spending_data):
    st.error(warning)

# ✅ 시간 기반 변화 탐지
if not df_all.empty:
    st.subheader("📈 3개월간 지출 변화 감지")
    for cat in categories:
        msg = detect_trends(df_all, cat, int(selected_month.replace("월", "")))
        if msg:
            st.warning(msg)

# ✅ 소비자 유형
st.subheader("🧠 소비자 유형 분석")
st.success(classify_user(spending_data))

# ✅ 클러스터링 유사 소비자 조언
st.subheader("👥 비슷한 소비자 조언")
st.info(cluster_feedback(spending_data))
