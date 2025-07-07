# ✅ Streamlit 시작 이후 코드 중간에 삽입

# ✅ 시간 기반 변화 탐지 함수
def detect_trend_increase(df_all, selected_month):
    trend_tips = []
    month_order = [f"{i}월" for i in range(1, 13)]
    current_idx = month_order.index(selected_month)
    if current_idx >= 2:
        recent_months = month_order[current_idx-2:current_idx+1]
        df_recent = df_all[df_all["month"].isin(recent_months)]
        for category in categories:
            trend = df_recent[df_recent["category"] == category].sort_values("month")
            if len(trend) == 3:
                values = trend["amount"].values
                if values[0] < values[1] < values[2]:
                    trend_tips.append(f"📈 최근 3개월간 **{category}** 지출이 꾸준히 증가하고 있어요.")
    return trend_tips

# ✅ 지출 이상치 감지 함수
def detect_outliers(df_all, selected_month):
    outlier_tips = []
    df_past = df_all[df_all["month"] != selected_month]
    if df_past.empty:
        return outlier_tips
    for category in categories:
        avg = df_past[df_past["category"] == category]["amount"].mean()
        current = df_all[(df_all["month"] == selected_month) & (df_all["category"] == category)]["amount"].values
        if current.size > 0 and avg > 0 and current[0] > avg * 1.5:
            outlier_tips.append(f"⚠️ **{category}** 지출이 평소보다 150% 이상 증가했어요!")
    return outlier_tips

# ✅ 조언 출력 섹션 아래에 추가
st.subheader("📉 기타 소비 분석")

# 시간 기반 변화 탐지 출력
trend_msgs = detect_trend_increase(df_all, selected_month)
for msg in trend_msgs:
    st.warning(msg)

# 이상치 감지 출력
outlier_msgs = detect_outliers(df_all, selected_month)
for msg in outlier_msgs:
    st.warning(msg)
