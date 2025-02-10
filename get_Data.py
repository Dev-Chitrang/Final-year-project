import yfinance as yf
import pandas as pd


def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    sp500_df = tables[0]
    sp500_companies = sp500_df[['Symbol', 'Security']].to_dict(orient='records')
    return sp500_companies


def get_financial_statements(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    
    def get_latest_two_years(df):
        if df is None or df.empty:
            return {}
        df = df.fillna(0)  # Replace NaN with 0
        years = df.columns[1]  # Get the latest two years (assuming chronological order)
        return df[years].to_dict()

    return {
        'income_statement': get_latest_two_years(stock.financials),
        'balance_sheet': get_latest_two_years(stock.balance_sheet),
        'cashflow': get_latest_two_years(stock.cashflow),
        'info': stock.info
    }

def get_financial_data(ticker_symbol):
    financial_statements = get_financial_statements(ticker_symbol)
    is_ = financial_statements['income_statement']
    bs = financial_statements['balance_sheet']
    cf = financial_statements['cashflow']
    info = financial_statements['info']

    def get_value(df, key):
        """Safely fetch a value from a dictionary"""
        if isinstance(df, dict) and key in df:
            val = df[key]
            if isinstance(val, dict):
                return list(val.values())[0]
            return val
        return 0

    # Fetch values safely
    total_assets = get_value(bs, 'Total Assets')
    cash = get_value(bs, 'Cash And Cash Equivalents')
    long_term_debt = get_value(bs, 'Long Term Debt')
    total_liabilities = get_value(bs, 'Total Liabilities Net Minority Interest')
    retained_earnings = get_value(bs, 'Retained Earnings')
    stockholders_equity = get_value(bs, 'Ordinary Shares Number')
    inventories_total = get_value(bs, 'Inventory')
    revenue_total = get_value(is_, 'Total Revenue')
    gross_profit = get_value(is_, 'Gross Profit')
    ebit = get_value(is_, 'EBIT')
    interest_expense = get_value(is_, 'Interest Expense')
    operating_cash_flow = get_value(cf, 'Operating Cash Flow')
    financing_cash_flow = get_value(cf, 'Financing Cash Flow')
    common_equity_liquidation = get_value(bs, 'Common Stock Equity')
    comprehensive_income_parent = get_value(is_, 'Comprehensive Income Net Of Tax')

    # Market and employee details
    market_value_total = info.get('marketCap', 0)
    book_value_per_share = info.get('bookValue', 0)
    employees = info.get('fullTimeEmployees', 0)
    shares_outstanding = info.get('sharesOutstanding', 0)

    # Calculate net cash flow
    net_cash_flow = operating_cash_flow + financing_cash_flow

    # Calculations
    debt_current_liabilities = total_liabilities - long_term_debt
    total_debt = long_term_debt + debt_current_liabilities
    total_debt_to_total_assets = total_debt / total_assets if total_assets else 0
    total_assets_to_total_liabilities = total_assets / total_liabilities if total_liabilities else 0
    ebit_to_total_assets = ebit / total_assets if total_assets else 0
    gross_profit_to_revenue = gross_profit / revenue_total if revenue_total else 0
    ebit_to_revenue = ebit / revenue_total if revenue_total else 0
    earnings_per_share_operations = operating_cash_flow / shares_outstanding if shares_outstanding else 0

    # Return results with missing values replaced by 0
    return {
        'Assets - Total': total_assets or 0,
        'Cash': cash or 0,
        'Debt in Current Liabilities - Total': debt_current_liabilities or 0,
        'Long-Term Debt - Total': long_term_debt or 0,
        'Earnings Before Interest': ebit or 0,
        'Gross Profit (Loss)': gross_profit or 0,
        'Liabilities - Total': total_liabilities or 0,
        'Retained Earnings': retained_earnings or 0,
        'Total debt/total asset': total_debt_to_total_assets or 0,
        'Total asset/total liabilities': total_assets_to_total_liabilities or 0,
        'EBTI/total asset': ebit_to_total_assets or 0,
        'Gross profit/revenue': gross_profit_to_revenue or 0,
        'EBTI/Revenue': ebit_to_revenue or 0,
        'Sales/Turnover (Net)': revenue_total or 0,
        'Stockholders Equity - Total': stockholders_equity or 0,
        'Interest and Related Expense - Total': interest_expense or 0,
        'Market Value - Total - Fiscal': market_value_total or 0,
        'Book Value Per Share': book_value_per_share or 0,
        'Common Equity - Liquidation Value': common_equity_liquidation or 0,
        'Comprehensive Income - Parent': comprehensive_income_parent or 0,
        'Employees': employees or 0,
        'Inventories - Total': inventories_total or 0,
        'Earnings Per Share from Operations': earnings_per_share_operations or 0,
        'Revenue - Total': revenue_total or 0,
        'Operating Activities - Net Cash Flow': operating_cash_flow or 0,
        'Financing Activities - Net Cash Flow': financing_cash_flow or 0,
        'Net Cash Flow': net_cash_flow or 0
    }


if __name__ == '__main__':
    ticker_symbol = "HTZ"
    financial_data = get_financial_data(ticker_symbol)
    print(financial_data)
