import logging
import os
from simulations.dca_simulation import run_dca_simulation
from simulations.bond_simulation import run_bond_simulation
from simulations.savings_simulation import run_savings_simulation  # Import the savings simulation
from datetime import timedelta

# Update logging configuration to include file and line number
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]"
)

SIMULATION_FUNCTIONS = {
    "dca_simulation": run_dca_simulation,
    "bond_simulation": run_bond_simulation,
    "savings_simulation": run_savings_simulation  # Add savings simulation
}

def run_simulations(params):
    """
    Runs all simulations for the given parameters, creating a separate account for each ticker.

    :param params: A dictionary containing simulation parameters:
                   - start_date: The start date of the simulation (YYYY-MM-DD).
                   - end_date: The end date of the simulation (YYYY-MM-DD).
                   - initial_investment: The initial investment amount.
                   - monthly_investment: The monthly investment amount.
                   - tickers: A list of selected stock tickers.
    :return: A dictionary where each key is a simulation name and the value is a list of accounts (one per simulation).
    """
    results = {}

    for simulation_name, simulation_function in SIMULATION_FUNCTIONS.items():
        try:
            # Pass the parameters dictionary directly to the simulation function
            simulation_results = simulation_function(params)
            results[simulation_name] = simulation_results
        except Exception as e:
            logging.error(f"Error running simulation '{simulation_name}': {e}", exc_info=True)
            results[simulation_name] = {"error": str(e)}

    return results  # Return results for all simulations
