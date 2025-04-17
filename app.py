import streamlit as st
import ra_calculator
import salary_calculator
import budget_tool
import retirement_calculator
import estate_liquidity
import everest_wealth

# Add custom CSS for grey background and white text to match Navigate Wealth logo
st.markdown(
    """
    <style>
    .stApp {
        background-color: #4A4A4A;
        color: white;
    }
    h1 {
        color: white;
    }
    .stTextInput > div > div > input {
        background-color: #555555;
        color: white;
    }
    .stTextInput > div > div > input::placeholder {
        color: #CCCCCC;
        opacity: 1;
    }
    .stNumberInput > div > div > input {
        background-color: #555555;
        color: white;
    }
    .stNumberInput > div > div > input::placeholder {
        color: #CCCCCC;
        opacity: 1;
    }
    .stButton > button {
        background-color: #666666;
        color: white;
        border: 1px solid #777777;
    }
    .stButton > button:hover {
        background-color: #777777;
        color: red;
    }
    .stFormSubmitButton > button {
        background-color: #666666;
        color: white;
        border: 1px solid #777777;
    }
    .stFormSubmitButton > button:hover {
        background-color: #777777;
        color: red;
    }
    .stDownloadButton > button {
        background-color: #666666;
        color: white;
        border: 1px solid #777777;
    }
    .stDownloadButton > button:hover {
        background-color: #777777;
        color: red;
    }
    .stAlert {
        background-color: #333333;
        color: white;
    }
    .stSelectbox > div > div > select {
        background-color: #333333;
        color: white;
    }
    .stTextInput > label, .stNumberInput > label, .stSelectbox > label {
        color: white;
    }
    .stMarkdown, .stMarkdown p {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Center the logo using columns
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", width=300)
st.markdown("<br>", unsafe_allow_html=True)
st.title("Navigate Wealth Financial Tools")
st.markdown("<p style='text-align: center; color: #CCCCCC;'>Powered by Navigate Wealth</p>", unsafe_allow_html=True)

# Tool selection dropdown
tool_options = ["Select a Tool", "Budget Tool", "Estate Liquidity Tool", "Everest Wealth", "RA Tax Rebate Calculator", "Retirement Calculator", "Salary Tax Calculator"]
# Sort tools alphabetically, keeping "Select a Tool" as the first option
tool_options = ["Select a Tool"] + sorted([tool for tool in tool_options if tool != "Select a Tool"])
selected_tool = st.selectbox("Choose a Financial Tool:", tool_options)

# Display the selected tool's interface
if selected_tool == "Select a Tool":
    st.write("Please select a tool from the dropdown above to get started.")
elif selected_tool == "RA Tax Rebate Calculator":
    ra_calculator.show()
elif selected_tool == "Salary Tax Calculator":
    salary_calculator.show()
elif selected_tool == "Budget Tool":
    budget_tool.show()
elif selected_tool == "Retirement Calculator":
    retirement_calculator.show()
elif selected_tool == "Estate Liquidity Tool":
    estate_liquidity.show()
elif selected_tool == "Everest Wealth":
    everest_wealth.show()
