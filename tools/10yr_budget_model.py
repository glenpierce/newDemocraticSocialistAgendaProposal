"""10-year parameterized budget projection model

Run: python3 tools/10yr_budget_model.py
Outputs: prints a summary and writes outputs/10yr_projection_[scenario].csv

All numbers are in billions of USD unless noted otherwise; GDP presented in billions.
"""
from pathlib import Path
import csv
from typing import Dict, List, Tuple

OUT_DIR = Path('outputs')
OUT_DIR.mkdir(exist_ok=True)

# Type aliases for clarity
Scenario = Dict[str, object]
Row = Dict[str, float]


def build_scenarios() -> Dict[str, Scenario]:
    """Return the predefined scenario parameter dictionaries.

    Each scenario dictionary contains model parameters and steady-state
    policy revenue/spending assumptions.
    """
    return {
        'conservative': {
            'years': 10,
            'nominal_gdp_growth': 0.025,
            'baseline_receipts_growth_premium': 0.015,
            'baseline_outlays_growth_premium': 0.02,
            'interest_rate_on_new_debt': 0.035,
            'initial_gdp': 31000.0,
            'baseline_receipts_initial': 5000.0,
            'baseline_outlays_initial': 7000.0,
            'wealth_tax_revenue_ss': 228.0,
            'corporate_tax_revenue_ss': 100.0,
            'capital_gains_revenue_ss': 80.0,
            'enforcement_revenue_ss': 50.0,
            'healthcare_net_spending_ss': 600.0,
            'investment_spending_ss': 400.0,
            'ramp_factors': [0.25, 0.5, 0.75, 1.0]
        },
        'central_balanced': {
            'years': 10,
            'nominal_gdp_growth': 0.03,
            'baseline_receipts_growth_premium': 0.01,
            'baseline_outlays_growth_premium': 0.01,
            'interest_rate_on_new_debt': 0.035,
            'initial_gdp': 31000.0,
            'baseline_receipts_initial': 5000.0,
            'baseline_outlays_initial': 7000.0,
            'wealth_tax_revenue_ss': 700.0,
            'corporate_tax_revenue_ss': 200.0,
            'capital_gains_revenue_ss': 150.0,
            'enforcement_revenue_ss': 120.0,
            'healthcare_net_spending_ss': 200.0,
            'investment_spending_ss': 350.0,
            'ramp_factors': [0.25, 0.5, 0.75, 1.0]
        },
        'optimistic': {
            'years': 10,
            'nominal_gdp_growth': 0.035,
            'baseline_receipts_growth_premium': 0.01,
            'baseline_outlays_growth_premium': 0.005,
            'interest_rate_on_new_debt': 0.03,
            'initial_gdp': 31000.0,
            'baseline_receipts_initial': 5000.0,
            'baseline_outlays_initial': 7000.0,
            'wealth_tax_revenue_ss': 900.0,
            'corporate_tax_revenue_ss': 250.0,
            'capital_gains_revenue_ss': 200.0,
            'enforcement_revenue_ss': 150.0,
            'healthcare_net_spending_ss': 150.0,
            'investment_spending_ss': 300.0,
            'ramp_factors': [0.3, 0.6, 0.9, 1.0]
        }
    }


def project_budget_over_horizon(scenario: Scenario) -> Tuple[List[Row], List[Row]]:
    """Project budget and baseline time series for the scenario.

    Returns a tuple: (projected_rows, baseline_only_rows).
    Both lists contain one row per year with rounded values.
    """
    years = int(scenario['years'])
    g = float(scenario['nominal_gdp_growth'])
    receipts_premium = float(scenario['baseline_receipts_growth_premium'])
    outlays_premium = float(scenario['baseline_outlays_growth_premium'])

    current_gdp = float(scenario['initial_gdp'])
    current_baseline_receipts = float(scenario['baseline_receipts_initial'])
    current_baseline_outlays = float(scenario['baseline_outlays_initial'])

    steady_policy_revenue = (
        float(scenario['wealth_tax_revenue_ss'])
        + float(scenario['corporate_tax_revenue_ss'])
        + float(scenario['capital_gains_revenue_ss'])
        + float(scenario['enforcement_revenue_ss'])
    )

    steady_policy_spending = (
        float(scenario['healthcare_net_spending_ss'])
        + float(scenario['investment_spending_ss'])
    )

    ramp_factors = list(scenario.get('ramp_factors', [1.0]))

    projected_rows: List[Row] = []
    baseline_rows: List[Row] = []

    for year in range(1, years + 1):
        # determine the policy ramp factor for this year
        ramp = ramp_factors[year - 1] if year <= len(ramp_factors) else 1.0

        policy_revenue_this_year = steady_policy_revenue * ramp
        policy_spending_this_year = steady_policy_spending * ramp

        total_receipts = current_baseline_receipts + policy_revenue_this_year
        total_outlays = current_baseline_outlays + policy_spending_this_year
        deficit = total_outlays - total_receipts

        # record the projected row
        projected_rows.append({
            'Year': year,
            'GDP': round(current_gdp, 1),
            'BaselineReceipts': round(current_baseline_receipts, 1),
            'BaselineOutlays': round(current_baseline_outlays, 1),
            'PolicyRevenue': round(policy_revenue_this_year, 1),
            'PolicySpending': round(policy_spending_this_year, 1),
            'TotalReceipts': round(total_receipts, 1),
            'TotalOutlays': round(total_outlays, 1),
            'Deficit': round(deficit, 1)
        })

        # record the baseline-only row for comparison
        baseline_rows.append({
            'Year': year,
            'GDP': round(current_gdp, 1),
            'BaselineReceipts': round(current_baseline_receipts, 1),
            'BaselineOutlays': round(current_baseline_outlays, 1),
            'BaselineDeficit': round(current_baseline_outlays - current_baseline_receipts, 1)
        })

        # update macro variables for the year (apply growth for next year's starting point)
        current_gdp *= (1 + g)
        current_baseline_receipts *= (1 + g + receipts_premium)
        current_baseline_outlays *= (1 + g + outlays_premium)

    return projected_rows, baseline_rows


def write_rows_to_csv(rows: List[Row], csv_path: Path) -> None:
    """Write a list of row dictionaries to CSV using the provided Path."""
    if not rows:
        raise ValueError('No rows to write to CSV')

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def compute_cumulative_metrics(projected_rows: List[Row], baseline_rows: List[Row]) -> Dict[str, float]:
    """Compute cumulative deficits and the policy net impact over the horizon."""
    cumulative_projected_deficit = sum(r['Deficit'] for r in projected_rows)
    cumulative_baseline_deficit = sum(r['BaselineDeficit'] for r in baseline_rows)
    cumulative_policy_net = cumulative_projected_deficit - cumulative_baseline_deficit

    return {
        'cumulative_projected_deficit': round(cumulative_projected_deficit, 1),
        'cumulative_baseline_deficit': round(cumulative_baseline_deficit, 1),
        'cumulative_policy_net': round(cumulative_policy_net, 1),
        'final_year_deficit': projected_rows[-1]['Deficit'] if projected_rows else 0.0
    }


def main() -> None:
    scenarios = build_scenarios()
    summaries = {}

    for name, params in scenarios.items():
        projected, baseline = project_budget_over_horizon(params)
        csv_file = OUT_DIR / f'10yr_projection_{name}.csv'
        write_rows_to_csv(projected, csv_file)

        metrics = compute_cumulative_metrics(projected, baseline)
        summaries[name] = {
            'csv': str(csv_file),
            **metrics
        }

    # print a concise human-readable summary
    print('10-year scenario summaries:')
    for scenario_name, m in summaries.items():
        print(
            f"- {scenario_name}: CSV={m['csv']}, "
            f"cum_projected_deficit={m['cumulative_projected_deficit']} bn, "
            f"baseline_deficit={m['cumulative_baseline_deficit']} bn, "
            f"policy_net={m['cumulative_policy_net']} bn, "
            f"final_deficit={m['final_year_deficit']} bn"
        )

    print('\nNote: "policy_net" is the cumulative difference between the projected deficits under the scenario and the baseline-only deficits (positive = worse than baseline).')

    # write a short README in outputs for quick guidance
    readme_path = OUT_DIR / 'README.txt'
    with readme_path.open('w') as f:
        f.write('This folder contains the 10-year projection CSVs produced by tools/10yr_budget_model.py\n')
        f.write('Adjust parameters in the script and re-run to explore scenarios.\n')


if __name__ == '__main__':
    main()

