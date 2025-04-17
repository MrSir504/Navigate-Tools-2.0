import streamlit as st
import pandas as pd
import io

# Tax Rates and Rebates (2024/2025)
TAX_BRACKETS = [
    (0, 237100, 0.18, 0),
    (237101, 370500, 0.26, 42678),
    (370501, 512800, 0.31, 77362),
    (512801, 673000, 0.36, 121475),
    (673001, 857900, 0.39, 179147),
    (857901, 1817000, 0.41, 251258),
    (1817001, float('inf'), 0.45, 644489)
]
REBATES = {
    "primary": 17235,
    "secondary": 9444,
    "tertiary": 3145
}

def get_tax_rate(income):
    """Return the marginal tax rate based on annual taxable income (2024/2025 rates)."""
    for lower, upper, rate, base_tax in TAX_BRACKETS:
        if lower <= income <= upper:
            return rate
    return 0.45

def calculate_ra_rebate(income, contribution):
    """Calculate the tax rebate for RA contributions and excess carryover."""
    max_deductible = min(income * 0.275, 350000)
    deductible = min(contribution, max_deductible)
    excess = max(0, contribution - max_deductible)
    tax_rate = get_tax_rate(income)
    rebate = deductible * tax_rate
    return deductible, tax_rate, rebate, excess

def show():
    st.write("Enter client details to calculate their tax rebate for retirement annuity contributions.")
    st.markdown(
        "<p style='font-size: 14px; font-style: italic; color: #CCCCCC;'>RA Contribution Limits: You can deduct RA contributions up to 27.5% of your taxable income, capped at R350,000 per year. Excess contributions roll over to future years. Verify limits for the 2025/2026 tax year.</p>",
        unsafe_allow_html=True
    )

    name = st.text_input("Client's Name")
    income = st.number_input("Annual Pensionable Income (R)", min_value=0.0, step=1000.0)
    contribution = st.number_input("Annual RA Contribution (R)", min_value=0.0, step=1000.0)

    if st.button("Calculate Rebate"):
        if not name.strip():
            st.error("Please enter a name.")
        elif income < 0 or contribution < 0:
            st.error("Income and contribution must be non-negative.")
        else:
            try:
                deductible, tax_rate, rebate, excess = calculate_ra_rebate(income, contribution)
                st.success("--- Tax Rebate Summary ---")
                st.write(f"**Client**: {name}")
                st.write(f"**Annual Pensionable Income**: R {income:,.2f}")
                st.write(f"**RA Contribution**: R {contribution:,.2f}")
                st.write(f"**Deductible Contribution**: R {deductible:,.2f}")
                if excess > 0:
                    st.write(f"**Excess Contribution (Carried Over)**: R {excess:,.2f}")
                st.write(f"**Marginal Tax Rate**: {tax_rate * 100:.1f}%")
                st.write(f"**Tax Rebate**: R {rebate:,.2f}")
                st.markdown(
                    "<p style='font-size: 14px; color: #888888;'>Note: Tax rates are based on 2024/2025 SARS tables. Verify with 2025/2026 rates when available.</p>",
                    unsafe_allow_html=True
                )
                summary_data = {
                    "Client": [name],
                    "Annual Pensionable Income (R)": [income],
                    "RA Contribution (R)": [contribution],
                    "Deductible Contribution (R)": [deductible],
                    "Excess Contribution (Carried Over) (R)": [excess if excess > 0 else 0],
                    "Marginal Tax Rate (%)": [tax_rate * 100],
                    "Tax Rebate (R)": [rebate]
                }
                df = pd.DataFrame(summary_data)
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name="RA Tax Rebate Summary")
                    instructions = pd.DataFrame({
                        "Instructions": [
                            "This Excel file contains your RA Tax Rebate Summary.",
                            "There are no charts in this tool, but you can create your own in Excel.",
                            "For example, select your data and use Insert > Chart to visualize your results."
                        ]
                    })
                    instructions.to_excel(writer, index=False, sheet_name="Instructions")
                buffer.seek(0)
                st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name="ra_tax_rebate_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error: {e}")