# ✅ 소비 분석 함수 수정
def analyze_spending(spending_data, monthly_budget):
    total_spent = sum(item["amount"] for item in spending_data)
    tips = []

    if total_spent > monthly_budget:
        tips.append(f"⚠️ 예산 초과! 설정한 월 예산({monthly_budget:,}원)을 {total_spent - monthly_budget:,}원 초과했습니다.")
    elif total_spent > monthly_budget * 0.9:
        tips.append("⚠️ 예산의 90% 이상 지출했습니다. 남은 기간 동안 지출을 줄이세요.")
    else:
        tips.append("✅ 예산 내에서 잘 지출하고 있습니다. 좋은 소비 습관입니다!")
        # ✅ 저축 조언 추가
        surplus = monthly_budget - total_spent
        if surplus > 0:
            tips.append(f"🎯 이번 달 예산의 {surplus:,}원이 남았습니다. 남은 금액은 비상금 계좌나 예적금으로 저축해보는 건 어떨까요?")

    # ✅ 카테고리별 소비 조언 및 습관
    for item in spending_data:
        category = item["category"]
        amount = item["amount"]

        if category == "카페" and amount > 70000:
            tips.append("☕ 카페 소비가 많습니다. 직접 커피 내려 마시기 같은 작은 실천으로도 절약할 수 있어요.")
        elif category == "쇼핑" and amount > 100000:
            tips.append("🛍️ 쇼핑 지출이 높습니다. 매달 ‘소비하지 않는 날(No-Spend Day)’을 정해보세요.")
        elif category == "식비" and amount > 200000:
            tips.append("🍱 식비 지출이 많다면 일주일에 하루는 도시락을 싸거나 집밥 위주로 구성해보세요.")
        elif category == "여가" and amount > 100000:
            tips.append("🎮 여가비가 높다면 무료 야외활동, 도서관 이용 등을 고려해보세요.")
        elif category == "교통" and amount > 80000:
            tips.append("🚌 교통비가 높습니다. 정기권 활용을 고려해보세요.")

    return tips
