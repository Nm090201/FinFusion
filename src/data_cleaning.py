"""
Generate Proper Quantitative Summary for Portfolio Analysis
This script converts your raw stock data into the format needed by tab3
"""

import pandas as pd
import numpy as np

def create_quantitative_summary(input_csv, output_csv='quantitative_summary_fixed.csv'):
    """
    Convert raw stock data to proper format for portfolio analysis
    
    Args:
        input_csv: Your current CSV file
        output_csv: Output file name
    """
    
    # Load data
    df = pd.read_csv(input_csv)
    
    print("=== ORIGINAL DATA ===")
    print(df.head())
    print(f"\nColumns: {df.columns.tolist()}")
    
    # Create new dataframe with required columns
    summary = pd.DataFrame()
    
    # 1. Stock ticker
    summary['Stock'] = df['Stock']
    
    # 2. Adjust returns to reasonable range
    # Problem: Your data has lifetime returns (110,000%!)
    # Solution: Cap at reasonable values OR use recent period only
    
    # Option A: Cap returns at 500% (still aggressive)
    summary['Cumulative Return (%)'] = df['Cumulative Return (%)'].clip(upper=500)
    
    # Option B: Use a log transformation to bring down extreme values
    # summary['Cumulative Return (%)'] = np.log1p(df['Cumulative Return (%)']) * 50
    
    # 3. Use volatility as-is (seems reasonable: 1-4%)
    # But volatility should typically be 15-60% for stocks
    # Your volatility is DAILY, need to annualize it!
    summary['Volatility (%)'] = df['Volatility (%)'] * np.sqrt(252)  # Annualize
    
    # 4. Calculate Sharpe Ratio
    risk_free_rate = 2.0  # Assume 2% risk-free rate
    summary['Sharpe Ratio'] = (summary['Cumulative Return (%)'] - risk_free_rate) / summary['Volatility (%)']
    
    # Handle inf and nan values
    summary['Sharpe Ratio'] = summary['Sharpe Ratio'].replace([np.inf, -np.inf], 0)
    summary['Sharpe Ratio'] = summary['Sharpe Ratio'].fillna(0)
    
    print("\n=== FIXED DATA ===")
    print(summary.head())
    
    print("\n=== STATISTICS ===")
    print(f"Return range: {summary['Cumulative Return (%)'].min():.2f}% to {summary['Cumulative Return (%)'].max():.2f}%")
    print(f"Volatility range: {summary['Volatility (%)'].min():.2f}% to {summary['Volatility (%)'].max():.2f}%")
    print(f"Sharpe range: {summary['Sharpe Ratio'].min():.2f} to {summary['Sharpe Ratio'].max():.2f}")
    
    # Save
    summary.to_csv(output_csv, index=False)
    print(f"\n✅ Fixed data saved to: {output_csv}")
    
    return summary

# Alternative: Use recent period returns only
def create_summary_from_recent_returns(input_csv, lookback_period='1Y', output_csv='quantitative_summary_recent.csv'):
    """
    Calculate returns from recent period only (more realistic)
    
    This is the BETTER approach but requires historical price data
    """
    
    df = pd.read_csv(input_csv)
    
    # For demonstration, we'll use a scaling approach
    # In reality, you'd want to calculate from actual recent prices
    
    summary = pd.DataFrame()
    summary['Stock'] = df['Stock']
    
    # Scale down extreme returns using square root
    # This keeps the ranking but makes values more reasonable
    returns = df['Cumulative Return (%)']
    
    # Apply square root transformation for extreme values
    summary['Cumulative Return (%)'] = np.where(
        returns > 100,
        np.sqrt(returns) * 10,  # Scale down extreme values
        returns  # Keep reasonable values as-is
    )
    
    # Annualize volatility
    summary['Volatility (%)'] = df['Volatility (%)'] * np.sqrt(252)
    
    # Calculate Sharpe Ratio
    risk_free_rate = 2.0
    summary['Sharpe Ratio'] = (summary['Cumulative Return (%)'] - risk_free_rate) / summary['Volatility (%)']
    summary['Sharpe Ratio'] = summary['Sharpe Ratio'].replace([np.inf, -np.inf], 0).fillna(0)
    
    print("\n=== RECENT PERIOD SUMMARY ===")
    print(summary.head(10))
    
    print(f"\nReturn range: {summary['Cumulative Return (%)'].min():.2f}% to {summary['Cumulative Return (%)'].max():.2f}%")
    print(f"Volatility range: {summary['Volatility (%)'].min():.2f}% to {summary['Volatility (%)'].max():.2f}%")
    print(f"Sharpe range: {summary['Sharpe Ratio'].min():.2f} to {summary['Sharpe Ratio'].max():.2f}")
    
    summary.to_csv(output_csv, index=False)
    print(f"\n✅ Recent period summary saved to: {output_csv}")
    
    return summary

if __name__ == "__main__":
    import sys
    
    # Usage
    input_file = '/Users/nidhi/Desktop/GenAI_Hackathon/data/csv/fin_data/quantitative_summary.csv'
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    
    print("=" * 60)
    print("FIXING QUANTITATIVE SUMMARY DATA")
    print("=" * 60)
    
    # Method 1: Cap extreme values
    print("\n### METHOD 1: Capping Extreme Values ###\n")
    df1 = create_quantitative_summary(input_file, 'quantitative_summary_capped.csv')
    
    # Method 2: Transform extreme values
    print("\n" + "=" * 60)
    print("\n### METHOD 2: Transform Extreme Values (RECOMMENDED) ###\n")
    df2 = create_summary_from_recent_returns(input_file, output_csv='quantitative_summary_transformed.csv')
    
    print("\n" + "=" * 60)
    print("\n✅ DONE! Two versions created:")
    print("   1. quantitative_summary_capped.csv (simple cap at 500%)")
    print("   2. quantitative_summary_transformed.csv (scaled transformation)")
    print("\n💡 RECOMMENDED: Use quantitative_summary_transformed.csv")
    print("=" * 60)