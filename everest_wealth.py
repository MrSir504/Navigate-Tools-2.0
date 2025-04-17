import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# Constants for Everest Wealth Products
ONYX_INCOME_PLUS_RATE = 0.142  # 14.2% annual return
STRATEGIC_INCOME_RATE = 0.128  # 12.8% annual return
DIVIDEND_TAX_RATE = 0.20  # 20% dividend tax
TERM_YEARS = 5
STRATEGIC_INCOME_BONUS = 0.10  # 10% special dividend bonus at the end of term
ONYX_BROKER_COMMISSION = 0.04  # 4% commission for Onyx Income Plus
STRATEGIC_BROKER_COMMISSION = 0.05  # 5% commission for Strategic Income
MINIMUM_INVESTMENT = 100000  # R100,000 minimum
INVESTMENT_INCREMENT = 5000  # Must be divisible by R5,000

def calculate_investment_results(investment_amount, product):
    """Calculate gross and net returns for the selected Everest Wealth product."""
    # Determine the annual rate and broker commission based on the product
    if product == "Onyx Income Plus":
        annual_rate = ONYX_INCOME_PLUS_RATE
        broker_commission_rate = ONYX_BROKER_COMMISSION
        special_bonus = 0  # No bonus for Onyx Income Plus
    else:  # Strategic Income
        annual_rate = STRATEGIC_INCOME_RATE
        broker_commission_rate = STRATEGIC_BROKER_COMMISSION
        special_bonus = investment_amount * STRATEGIC_INCOME_BONUS  # 10% bonus

    # Calculate broker fee
    broker_fee = investment_amount * broker_commission_rate

    # Gross returns
    gross_annual_return = investment_amount * annual_rate
    gross_monthly_income = gross_annual_return / 12
    gross_total_return = (gross_annual_return * TERM_YEARS) + special_bonus  # Include bonus for Strategic Income

    # Net returns after dividend tax
    net_monthly_income = gross_monthly_income * (1 - DIVIDEND_TAX_RATE)
    net_annual_return = net_monthly_income * 12
    net_bonus = special_bonus * (1 - DIVIDEND_TAX_RATE) if special_bonus > 0 else 0
    net_total_return = (net_annual_return * TERM_YEARS) + net_bonus  # Include net bonus

    return {
        "gross_monthly_income": gross_monthly_income,
        "gross_annual_return": gross_annual_return,
        "gross_total_return": gross_total_return,
        "net_monthly_income": net_monthly_income,
        "net_annual_return": net_annual_return,
        "net_total_return": net_total_return,
        "broker_fee": broker_fee
    }

def show():
    st.write("Calculate returns for Everest Wealth investment products.")
    st.markdown(
        "<p style='font-size: 14px; font-style: italic; color: #CCCCCC;'>Note: Returns are based on fixed rates for Onyx Income Plus (14.2% p.a.) and Strategic Income (12.8% p.a.) over a 5-year term. Dividend tax is deducted at 20%. Verify with Everest Wealth for your specific case.</p>",
        unsafe_allow_html=True
    )

    # Client name input
    name = st.text_input("Client's Name", key="everest_wealth_name")

    # Product selection
    product = st.selectbox("Select Everest Wealth Product", ["Onyx Income Plus", "Strategic Income"])

    # Investment amount input with validation
    investment_amount = st.number_input(
        "Investment Amount (R)",
        min_value=MINIMUM_INVESTMENT,
        step=INVESTMENT_INCREMENT,
        value=MINIMUM_INVESTMENT,
        help="Minimum investment is R100,000, and the amount must be divisible by R5,000."
    )

    # Validate that the investment amount is divisible by 5,000
    if investment_amount % INVESTMENT_INCREMENT != 0:
        st.error(f"Investment amount must be divisible by R{INVESTMENT_INCREMENT:,}. For example, R{investment_amount - (investment_amount % INVESTMENT_INCREMENT):,} or R{(investment_amount + INVESTMENT_INCREMENT - (investment_amount % INVESTMENT_INCREMENT)):,}.")
        return

    if st.button("Calculate Investment Returns"):
        if not name.strip():
            st.error("Please enter a name.")
        elif investment_amount < MINIMUM_INVESTMENT:
            st.error(f"Investment amount must be at least R{MINIMUM_INVESTMENT:,}.")
        else:
            try:
                # Calculate results
                results = calculate_investment_results(investment_amount, product)

                # Display summary
                st.success("--- Everest Wealth Investment Summary ---")
                st.write(f"**Client**: {name}")
                st.write(f"**Product**: {product}")
                st.write(f"**Investment Amount**: R {investment_amount:,.2f}")

                # Summary table with improved styling
                summary_data = {
                    "Metric": [
                        "Gross Monthly Income (R)",
                        "Gross Annual Return (R)",
                        "Gross Total Return Over Term (R)",
                        "Net Monthly Income (R)",
                        "Net Annual Return (R)",
                        "Net Total Return Over Term (R)",
                        "Broker Fee Earned (R)"
                    ],
                    "Value": [
                        results["gross_monthly_income"],
                        results["gross_annual_return"],
                        results["gross_total_return"],
                        results["net_monthly_income"],
                        results["net_annual_return"],
                        results["net_total_return"],
                        results["broker_fee"]
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df["Value"] = summary_df["Value"].apply(lambda x: f"R {x:,.2f}")

                # Add custom CSS for the dataframe to improve visibility
                st.markdown(
                    """
                    <style>
                    .dataframe {
                        background-color: #555555;
                        color: white;
                        border: 1px solid #777777;
                    }
                    .dataframe th {
                        background-color: #666666;
                        color: white;
                        border: 1px solid #777777;
                    }
                    .dataframe td {
                        background-color: #555555;
                        color: white;
                        border: 1px solid #777777;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                st.write("**Investment Returns**")
                st.dataframe(summary_df, use_container_width=True)

                # Bar chart for gross vs net monthly income
                fig = go.Figure(data=[
                    go.Bar(name="Gross Monthly Income", x=["Gross"], y=[results["gross_monthly_income"]], marker_color="#1f77b4"),
                    go.Bar(name="Net Monthly Income", x=["Net"], y=[results["net_monthly_income"]], marker_color="#ff7f0e")
                ])
                fig.update_layout(
                    title="Gross vs Net Monthly Income",
                    xaxis_title="Income Type",
                    yaxis_title="Amount (R)",
                    barmode="group",
                    showlegend=True
                )
                st.plotly_chart(fig)

                # Additional note for Strategic Income
                if product == "Strategic Income":
                    bonus = investment_amount * STRATEGIC_INCOME_BONUS
                    net_bonus = bonus * (1 - DIVIDEND_TAX_RATE)
                    st.write(f"**Note**: Strategic Income includes a special dividend bonus of R {bonus:,.2f} (Net: R {net_bonus:,.2f} after 20% dividend tax) at the end of the term.")

                # Downloadable summary
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    summary_df.to_excel(writer, index=False, sheet_name="Everest Wealth Summary")
                    instructions = pd.DataFrame({
                        "Instructions": [
                            "This Excel file contains your Everest Wealth Investment Summary.",
                            "The bar chart compares Gross vs Net Monthly Income.",
                            "You can recreate the chart in Excel by selecting the Gross and Net Monthly Income rows and using Insert > Bar Chart."
                        ]
                    })
                    instructions.to_excel(writer, index=False, sheet_name="Instructions")
                buffer.seek(0)
                st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name="everest_wealth_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    show()
