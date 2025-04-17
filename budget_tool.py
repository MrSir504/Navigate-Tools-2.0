import streamlit as st
import pandas as pd
import io

def calculate_budget(monthly_income, expenses):
    """Calculate total expenses, remaining budget, and savings potential."""
    total_expenses = sum(expense for category, expense in expenses)
    remaining_budget = monthly_income - total_expenses
    savings_potential = max(0, remaining_budget)
    return total_expenses, remaining_budget, savings_potential

def show():
    st.write("Enter your monthly income and expenses to create a budget and see your savings potential.")
    monthly_income = st.number_input("Monthly Income (R)", min_value=0.0, step=1000.0, value=39500.0)
    st.write("**Add Your Monthly Expenses**")
    with st.form(key="expense_form"):
        num_expenses = st.number_input("Number of Expense Categories", min_value=1, max_value=10, step=1, value=3)
        expenses = []
        for i in range(num_expenses):
            col1, col2 = st.columns(2)
            with col1:
                category = st.text_input(f"Expense Category {i+1}", value=f"Category {i+1}", key=f"category_{i}")
            with col2:
                amount = st.number_input(f"Amount (R)", min_value=0.0, step=100.0, key=f"amount_{i}")
            expenses.append((category, amount))
        submit_button = st.form_submit_button("Calculate Budget")

    if submit_button:
        if monthly_income < 0:
            st.error("Monthly income must be non-negative.")
        else:
            try:
                total_expenses, remaining_budget, savings_potential = calculate_budget(monthly_income, expenses)
                st.success("--- Budget Summary ---")
                st.write(f"**Monthly Income**: R {monthly_income:,.2f}")
                st.write("**Expenses Breakdown**:")
                expenses_data = []
                for category, amount in expenses:
                    st.write(f"- {category}: R {amount:,.2f}")
                    expenses_data.append({"Category": category, "Amount (R)": amount})
                st.write(f"**Total Monthly Expenses**: R {total_expenses:,.2f}")
                st.write(f"**Remaining Budget**: R {remaining_budget:,.2f}")
                summary_data = {
                    "Monthly Income (R)": [monthly_income],
                    "Total Monthly Expenses (R)": [total_expenses],
                    "Remaining Budget (R)": [remaining_budget]
                }
                if remaining_budget < 0:
                    st.warning("You're overspending! Consider reducing expenses to avoid debt.")
                else:
                    st.write(f"**Savings Potential**: R {savings_potential:,.2f}")
                    summary_data["Savings Potential (R)"] = [savings_potential]
                st.write("**Budget Breakdown Visualization**")
                chart_data = pd.DataFrame({
                    "Category": [category for category, amount in expenses] + ["Remaining Budget"],
                    "Amount (R)": [amount for category, amount in expenses] + [max(0, remaining_budget)]
                })
                st.bar_chart(chart_data.set_index("Category"))
                summary_df = pd.DataFrame(summary_data)
                expenses_df = pd.DataFrame(expenses_data)
                chart_df = pd.DataFrame(chart_data).reset_index()
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    summary_df.to_excel(writer, index=False, sheet_name="Budget Summary")
                    expenses_df.to_excel(writer, startrow=len(summary_df) + 2, index=False, sheet_name="Budget Summary")
                    chart_df.to_excel(writer, index=False, sheet_name="Chart Data", startrow=0)
                    instructions = pd.DataFrame({
                        "Instructions": [
                            "This Excel file contains your Budget Summary and Chart Data.",
                            "To recreate the bar chart in Excel:",
                            "1. Go to the 'Chart Data' sheet.",
                            "2. Select the 'Category' and 'Amount (R)' columns.",
                            "3. Click Insert > Bar Chart in Excel to visualize the budget breakdown."
                        ]
                    })
                    instructions.to_excel(writer, index=False, sheet_name="Instructions")
                buffer.seek(0)
                st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name="budget_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error: {e}")