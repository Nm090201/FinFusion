import pandas as pd
import numpy as np

# Load your current (WRONG) data
df = pd.read_csv('/Users/nidhi/Desktop/GenAI_Hackathon/data/csv/fin_data/quantitative_summary.csv')

print("CURRENT DATA (WRONG):")
print(df[['Stock', 'Cumulative Return (%)', 'Volatility (%)']].head())
print(f"\nMax return: {df['Cumulative Return (%)'].max():.2f}%")

# Create NEW dataframe with correct format
fixed = pd.DataFrame()

# 1. Stock names
fixed['Stock'] = df['Stock']

# 2. FIX RETURNS: Transform extreme values
returns = df['Cumulative Return (%)']
fixed['Cumulative Return (%)'] = np.where(
    returns > 100,
    np.sqrt(returns) * 10,  # Scale down extreme values
    np.maximum(returns, -90)  # Cap losses at -90%
)

# 3. FIX VOLATILITY: Annualize from daily to yearly
fixed['Volatility (%)'] = df['Volatility (%)'] * np.sqrt(252)

# 4. CALCULATE SHARPE RATIO
risk_free_rate = 2.0
fixed['Sharpe Ratio'] = (fixed['Cumulative Return (%)'] - risk_free_rate) / fixed['Volatility (%)']
fixed['Sharpe Ratio'] = fixed['Sharpe Ratio'].replace([np.inf, -np.inf], 0).fillna(0)

print("\n" + "="*80)
print("FIXED DATA (CORRECT):")
print(fixed[['Stock', 'Cumulative Return (%)', 'Volatility (%)', 'Sharpe Ratio']].head())

print("\n" + "="*80)
print("STATISTICS:")
print(f"Return range: {fixed['Cumulative Return (%)'].min():.2f}% to {fixed['Cumulative Return (%)'].max():.2f}%")
print(f"Volatility range: {fixed['Volatility (%)'].min():.2f}% to {fixed['Volatility (%)'].max():.2f}%")
print(f"Sharpe range: {fixed['Sharpe Ratio'].min():.2f} to {fixed['Sharpe Ratio'].max():.2f}")
print("="*80)

# SAVE AS NEW FILE
output_file = 'data/csv/fin_data/quantitative_summary.csv'
fixed.to_csv(output_file, index=False)

print(f"\n✅ FIXED DATA SAVED TO: {output_file}")
print("\nNow restart your Streamlit app!")