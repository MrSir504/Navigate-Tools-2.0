import streamlit as st
import pandas as pd
import io
import math
import plotly.graph_objects as go

def calculate_future_value(current_value, annual_rate, years, monthly_contribution=0, annual_contribution_increase=0):
    """Calculate the future value of an investment with monthly contributions and annual increases."""
    future_value = current_value
    monthly_rate = (1 + annual_rate) ** (1/12) - 1
    annual_contributions = monthly_contribution * 12
    for year in range(years):
        future_value = future_value * (1 + annual_rate)
        for month in range(12):
            monthly_contrib = (annual_contributions / 12) * (1 + monthly_rate) ** (11 - month)
            future_value += monthly_contrib
        annual_contributions *= (1 + annual_contribution_increase)
    return future_value

def calculate_years_until_depletion(capital, annual_income, inflation_rate, years_to_retirement, assumed_return):
    """Calculate how many years the capital will last with annual withdrawals."""
    current_capital = capital
    max_drawdown_rate = 0.175
    years = 0
    first_withdrawal = None
    capital_over_time = [current_capital]
    withdrawals_over_time = []
    monthly_income_over_time = []
    monthly_income_today_value = []
    while current_capital > 0:
        if current_capital <= 125000:
            withdrawals_over_time.append(current_capital)
            monthly_income = current_capital / 12
            monthly_income_over_time.append(monthly_income)
            total_years = years_to_retirement + years + 1
            inflation_factor = (1 + inflation_rate) ** total_years
            monthly_income_today = monthly_income / inflation_factor
            monthly_income_today_value.append(monthly_income_today)
            years += 1
            capital_over_time.append(0)
            withdrawals_over_time.append(0)
            monthly_income_over_time.append(0)
            monthly_income_today_value.append(0)
            break
        max_withdrawal = current_capital * max_drawdown_rate
        withdrawal = min(annual_income, max_withdrawal)
        if years == 0:
            first_withdrawal = withdrawal
        current_capital -= withdrawal
        current_capital = current_capital * (1 + assumed_return)
        years += 1
        capital_over_time.append(max(0, current_capital))
        withdrawals_over_time.append(withdrawal)
        monthly_income = withdrawal / 12
        monthly_income_over_time.append(monthly_income)
        total_years = years_to_retirement + years
        inflation_factor = (1 + inflation_rate) ** total_years
        monthly_income_today = monthly_income / inflation_factor
        monthly_income_today_value.append(monthly_income_today)
    return years, first_withdrawal, capital_over_time, withdrawals_over_time, monthly_income_over_time, monthly_income_today_value

def calculate_additional_savings_needed(shortfall, years_to_retirement, average_return):
    """Calculate additional monthly savings needed to bridge the shortfall."""
    if shortfall <= 0:
        return 0
    annual_rate = average_return
    fv_factor = ((1 + annual_rate) ** years_to_retirement - 1) / annual_rate
    annual_savings = shortfall / fv_factor
    monthly_savings = annual_savings / 12
    return monthly_savings

def calculate_retirement_plan(monthly_income, inflation_rate, annual_increase, years_to_retirement, preserve_capital, preservation_years, assumed_return):
    """Calculate the retirement plan details."""
    annual_income = monthly_income * 12
    future_annual_income = annual_income * (1 + inflation_rate) ** years_to_retirement * (1 + annual_increase) ** years_to_retirement
    future_monthly_income = future_annual_income / 12
    if preserve_capital:
        if assumed_return <= 0:
            capital_at_retirement = float('inf')
        else:
            capital_at_retirement = future_annual_income / assumed_return
            withdrawal_rate = future_annual_income / capital_at_retirement
            max_drawdown_rate = 0.175
            if withdrawal_rate > max_drawdown_rate:
                capital_at_retirement = future_annual_income / max_drawdown_rate
        remaining_years = 20
        income_after_preservation = future_annual_income * (1 + inflation_rate) ** preservation_years * (1 + annual_increase) ** preservation_years
        if assumed_return > 0:
            annuity_factor = (1 - (1 + assumed_return) ** (-remaining_years)) / assumed_return
            capital_required = income_after_preservation * annuity_factor
            capital_required = capital_required / (1 + assumed_return) ** preservation_years
            capital_required = max(capital_at_retirement, capital_required)
        else:
            capital_required = capital_at_retirement
        years_until_depletion = None
        withdrawal_at_retirement = min(future_annual_income, capital_required * max_drawdown_rate)
    else:
        capital_required = None
        years_until_depletion, withdrawal_at_retirement = None, future_annual_income
    return future_annual_income, future_monthly_income, capital_required, years_until_depletion, withdrawal_at_retirement

def show():
    st.write("Enter client details to calculate the capital needed for retirement.")
    name = st.text_input("Client's Name", key="retirement_calc_name")
    desired_monthly_income = st.number_input("Desired Monthly Income at Retirement (R)", min_value=0.0, step=1000.0)
    desired_annual_increase = st.number_input("Desired Annual Income Increase (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.5) / 100
    current_age = st.number_input("Current Age", min_value=18, max_value=100, step=1)
    retirement_age = st.selectbox("Retirement Age", [55, 60, 65])
    inflation_rate = st.number_input("Inflation Rate (%)", min_value=0.0, max_value=20.0, value=6.0, step=0.5) / 100
    assumed_return = st.number_input("Assumed Annual Return After Retirement (%)", min_value=0.0, max_value=20.0, value=7.0, step=0.5) / 100
    preserve_capital = st.checkbox("Preserve Capital at Retirement")
    preservation_years = 0
    if preserve_capital:
        preservation_years = st.selectbox("Preservation Period (Years)", [10, 15, 20, 25])
    provision_types = [
        "Retirement Annuity", "Pension Fund", "Provident Fund", "Preservation Fund",
        "Business", "Endowment", "Savings Fund", "Shares", "Linked Investment",
        "Property", "Fixed Deposit", "Other"
    ]
    st.write("**Add Your Current Provisions**")
    with st.form(key="provision_form"):
        num_provisions = st.number_input("Number of Provisions", min_value=1, max_value=10, step=1, value=1)
        provisions = []
        for i in range(num_provisions):
            st.write(f"**Provision {i+1}**")
            col1, col2 = st.columns(2)
            with col1:
                provision_type = st.selectbox(f"Provision Type {i+1}", provision_types, key=f"prov_type_{i}")
                current_value = st.number_input(f"Current Value (R)", min_value=0.0, step=1000.0, key=f"prov_value_{i}")
            with col2:
                annual_return = st.number_input(f"Assumed Annual Return (%)", min_value=0.0, max_value=20.0, value=7.0, step=0.5, key=f"prov_return_{i}") / 100
                monthly_contribution = st.number_input(f"Monthly Contribution (R)", min_value=0.0, step=100.0, key=f"prov_contrib_{i}")
            col3, col4 = st.columns(2)
            with col3:
                contribution_increase = st.number_input(f"Annual Contribution Increase (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.5, key=f"prov_increase_{i}") / 100
            provisions.append({
                "type": provision_type,
                "current_value": current_value,
                "annual_return": annual_return,
                "monthly_contribution": monthly_contribution,
                "contribution_increase": contribution_increase
            })
        submit_button = st.form_submit_button("Calculate Retirement Plan")

    if submit_button:
        if not name.strip():
            st.error("Please enter a name.")
        elif desired_monthly_income <= 0 or current_age < 18 or current_age >= retirement_age:
            st.error("Please ensure desired income is positive and current age is valid (18 or older, less than retirement age).")
        else:
            try:
                years_to_retirement = retirement_age - current_age
                future_annual_income, future_monthly_income, capital_required, years_until_depletion, withdrawal_at_retirement = calculate_retirement_plan(
                    desired_monthly_income, inflation_rate, desired_annual_increase, years_to_retirement, preserve_capital, preservation_years, assumed_return
                )
                total_provision_value = 0
                provisions_data = []
                average_return = 0
                total_weight = 0
                for provision in provisions:
                    fv = calculate_future_value(
                        provision["current_value"],
                        provision["annual_return"],
                        years_to_retirement,
                        provision["monthly_contribution"],
                        provision["contribution_increase"]
                    )
                    total_provision_value += fv
                    provisions_data.append({
                        "Type": provision["type"],
                        "Current Value (R)": provision["current_value"],
                        "Annual Return (%)": provision["annual_return"] * 100,
                        "Monthly Contribution (R)": provision["monthly_contribution"],
                        "Annual Contribution Increase (%)": provision["contribution_increase"] * 100,
                        "Future Value at Retirement (R)": fv
                    })
                    weight = provision["current_value"] + (provision["monthly_contribution"] * 12 * years_to_retirement)
                    average_return += provision["annual_return"] * weight
                    total_weight += weight
                if total_weight > 0:
                    average_return /= total_weight
                summary_data = {
                    "Client": [name],
                    "Current Age": [current_age],
                    "Retirement Age": [retirement_age],
                    "Years to Retirement": [years_to_retirement],
                    "Desired Monthly Income at Retirement (R)": [desired_monthly_income],
                    "Future Annual Income Needed (R)": [future_annual_income],
                    "Future Monthly Income Needed (R)": [future_monthly_income]
                }
                st.success("--- Retirement Plan Summary ---")
                st.write(f"**Client**: {name}")
                st.write(f"**Current Age**: {current_age}")
                st.write(f"**Retirement Age**: {retirement_age}")
                st.write(f"**Years to Retirement**: {years_to_retirement}")
                st.write(f"**Desired Monthly Income at Retirement (Today's Value)**: R {desired_monthly_income:,.2f}")
                st.write(f"**Future Annual Income Needed (Inflation Adjusted)**: R {future_annual_income:,.2f}")
                st.write(f"**Future Monthly Income Needed (Inflation Adjusted)**: R {future_monthly_income:,.2f}")
                st.write("**Provisions at Retirement**:")
                provisions_df = pd.DataFrame(provisions_data)
                st.write(provisions_df)
                st.write(f"**Total Future Value of Provisions**: R {total_provision_value:,.2f}")
                summary_data["Total Future Value of Provisions (R)"] = [total_provision_value]
                if preserve_capital:
                    shortfall = capital_required - total_provision_value
                    st.write(f"**Capital Required at Retirement (Preserve Capital)**: R {capital_required:,.2f}")
                    summary_data["Capital Required at Retirement (R)"] = [capital_required]
                    summary_data["Preserve Capital"] = ["Yes"]
                    summary_data["Preservation Period (Years)"] = [preservation_years]
                    st.write(f"**Initial Withdrawal at Retirement (Annual)**: R {withdrawal_at_retirement:,.2f}")
                    st.write(f"**Initial Withdrawal at Retirement (Monthly)**: R {(withdrawal_at_retirement / 12):,.2f}")
                    summary_data["Initial Withdrawal at Retirement (Annual) (R)"] = [withdrawal_at_retirement]
                    summary_data["Initial Withdrawal at Retirement (Monthly) (R)"] = [withdrawal_at_retirement / 12]
                else:
                    years_until_depletion, first_withdrawal, capital_over_time, withdrawals_over_time, monthly_income_over_time, monthly_income_today_value = calculate_years_until_depletion(
                        total_provision_value, future_annual_income, inflation_rate, years_to_retirement, assumed_return
                    )
                    st.write(f"**Capital at Retirement (Based on Provisions)**: R {total_provision_value:,.2f}")
                    st.write(f"**Years Until Capital Depletion**: {years_until_depletion}")
                    st.write(f"**Initial Withdrawal at Retirement (Annual)**: R {first_withdrawal:,.2f}")
                    st.write(f"**Initial Withdrawal at Retirement (Monthly)**: R {(first_withdrawal / 12):,.2f}")
                    summary_data["Capital at Retirement (R)"] = [total_provision_value]
                    summary_data["Years Until Capital Depletion"] = [years_until_depletion]
                    summary_data["Initial Withdrawal at Retirement (Annual) (R)"] = [first_withdrawal]
                    summary_data["Initial Withdrawal at Retirement (Monthly) (R)"] = [first_withdrawal / 12]
                    summary_data["Preserve Capital"] = ["No"]
                    summary_data["Preservation Period (Years)"] = [0]
                    st.write("**Capital Depletion Over Time**")
                    chart_data = pd.DataFrame({
                        "Age": list(range(retirement_age, retirement_age + len(capital_over_time))),
                        "Capital (R)": capital_over_time,
                        "Annual Withdrawal (R)": withdrawals_over_time,
                        "Monthly Income (R)": monthly_income_over_time,
                        "Monthly Income in Today's Value (R)": monthly_income_today_value
                    })
                    # First Graph: Capital and Annual Withdrawal
                    fig1 = go.Figure()
                    fig1.add_trace(go.Scatter(
                        x=chart_data["Age"],
                        y=chart_data["Capital (R)"],
                        mode="lines",
                        name="Capital (R)",
                        hovertemplate="Age: %{x}<br>Capital: R%{y:.2f}<extra></extra>"
                    ))
                    fig1.add_trace(go.Scatter(
                        x=chart_data["Age"],
                        y=chart_data["Annual Withdrawal (R)"],
                        mode="lines",
                        name="Annual Withdrawal (R)",
                        hovertemplate="Age: %{x}<br>Annual Withdrawal: R%{y:.2f}<extra></extra>"
                    ))
                    fig1.update_layout(
                        title="Capital and Annual Withdrawal Over Time",
                        xaxis_title="Age",
                        yaxis_title="Amount (R)",
                        hovermode="x unified",
                        showlegend=True
                    )
                    st.plotly_chart(fig1)

                    # Second Graph: Monthly Income (Future Value) and Monthly Income in Today's Value
                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(
                        x=chart_data["Age"],
                        y=chart_data["Monthly Income (R)"],
                        mode="lines",
                        name="Monthly Income (Future Value) (R)",
                        hovertemplate="Age: %{x}<br>Monthly Income (Future): R%{y:.2f}<extra></extra>"
                    ))
                    fig2.add_trace(go.Scatter(
                        x=chart_data["Age"],
                        y=chart_data["Monthly Income in Today's Value (R)"],
                        mode="lines",
                        name="Monthly Income in Today's Value (R)",
                        hovertemplate="Age: %{x}<br>Monthly Income (Today's Value): R%{y:.2f}<extra></extra>"
                    ))
                    fig2.update_layout(
                        title="Monthly Income Over Time",
                        xaxis_title="Age",
                        yaxis_title="Monthly Income (R)",
                        hovermode="x unified",
                        showlegend=True
                    )
                    st.plotly_chart(fig2)

                if preserve_capital and shortfall > 0:
                    additional_savings = calculate_additional_savings_needed(shortfall, years_to_retirement, average_return)
                    st.warning(f"**Capital Shortfall**: R {shortfall:,.2f}")
                    st.write(f"**Additional Monthly Savings Needed**: R {additional_savings:,.2f}")
                    summary_data["Capital Shortfall (R)"] = [shortfall]
                    summary_data["Additional Monthly Savings Needed (R)"] = [additional_savings]
                elif preserve_capital and shortfall <= 0:
                    st.write(f"**Capital Excess**: R {-shortfall:,.2f}")
                    summary_data["Capital Excess (R)"] = [-shortfall]
                    summary_data["Capital Shortfall (R)"] = [0]
                    summary_data["Additional Monthly Savings Needed (R)"] = [0]
                summary_df = pd.DataFrame(summary_data)
                chart_df = pd.DataFrame(chart_data).reset_index() if not preserve_capital else pd.DataFrame()
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    summary_df.to_excel(writer, index=False, sheet_name="Retirement Plan Summary")
                    provisions_df.to_excel(writer, startrow=len(summary_df) + 2, index=False, sheet_name="Retirement Plan Summary")
                    if not preserve_capital:
                        chart_df.to_excel(writer, index=False, sheet_name="Chart Data", startrow=0)
                    instructions = pd.DataFrame({
                        "Instructions": [
                            "This Excel file contains your Retirement Plan Summary and Provisions Data.",
                            "If you did not opt to preserve capital, the 'Chart Data' sheet includes data for visualizing capital depletion over time.",
                            "To recreate the line chart in Excel (if applicable):",
                            "1. Go to the 'Chart Data' sheet.",
                            "2. Select the 'Age' and 'Capital (R)' columns (or other metrics).",
                            "3. Click Insert > Line Chart in Excel to visualize the depletion."
                        ]
                    })
                    instructions.to_excel(writer, index=False, sheet_name="Instructions")
                buffer.seek(0)
                st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name="retirement_plan_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    show()
