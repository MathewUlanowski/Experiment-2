import logging
from flask import jsonify, render_template, request
from services.cache_service import clear_all_caches, search_tickers_with_cache, delete_data_cache_folder
from services.simulation_service import run_simulations, SIMULATION_FUNCTIONS  # Import SIMULATION_FUNCTIONS
from services.plotting_service import generate_plot  # Import the plotting service
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly.io as pio
import os

# Configure logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def setup_routes(app):
    """
    Sets up all the routes for the Flask application.

    :param app: The Flask application instance.
    """

    @app.route("/search_tickers", methods=["GET"])
    def search_tickers():
        try:
            query = request.args.get("query", "").strip()
            if not query:
                return jsonify({"error": "Query parameter is required."}), 400
            results = search_tickers_with_cache(query)
            # Ensure the response includes both symbol and full name
            tickers = [
                {"symbol": result["symbol"], "name": result["name"]}
                if isinstance(result, dict) and "symbol" in result and "name" in result
                else {"symbol": str(result), "name": ""}
                for result in results
            ]
            return jsonify({"results": tickers})
        except Exception as e:
            logging.error(f"Error in search_tickers: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/clear_cache", methods=["POST"])
    def clear_cache():
        try:
            clear_all_caches()
            return jsonify({"message": "Caches cleared successfully."}), 200
        except Exception as e:
            logging.error(f"Error in clear_cache: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/delete_data_cache", methods=["POST"])
    def delete_data_cache():
        try:
            delete_data_cache_folder()
            return jsonify({"message": "data_cache folder deleted successfully."}), 200
        except Exception as e:
            logging.error(f"Error in delete_data_cache: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/simulate", methods=["GET"])
    def simulate():
        """
        Runs selected simulations based on the provided parameters and returns Plotly data and layout.
        """
        try:
            # Collect errors
            errors = []

            # Run selected simulations and collect results
            all_balance_histories = []
            simulation_results = run_simulations(request.args.to_dict())

            for simulation, accounts in simulation_results.items():
                if isinstance(accounts, list):  # Ensure the simulation returned a list of accounts
                    for account in accounts:
                        if not hasattr(account, "balance_history"):
                            raise AttributeError(f"Account in simulation '{simulation}' does not have 'balance_history'.")
                        all_balance_histories.append((account.name, account.balance_history))
                else:
                    logging.error(f"Simulation '{simulation}' returned an error: {accounts.get('error')}")

            # Generate the Plotly graph using the plotting service
            fig = generate_plot(all_balance_histories)

            # Serialize the data and layout for JSON response
            data = [trace.to_plotly_json() for trace in fig.data]
            layout = fig.layout.to_plotly_json()

            # Return the data and layout as JSON
            return jsonify({"data": data, "layout": layout}), 200
        except Exception as e:
            logging.error(f"Error in simulate: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    @app.route("/available_simulations", methods=["GET"])
    def available_simulations():
        """
        Returns a list of available simulations based on the SIMULATION_FUNCTIONS dictionary.
        """
        try:
            simulations = [{"id": key, "name": key.replace("_", " ").title()} for key in SIMULATION_FUNCTIONS.keys()]
            return jsonify({"simulations": simulations})
        except Exception as e:
            logging.error(f"Error fetching available simulations: {e}")
            return jsonify({"error": "Failed to fetch available simulations"}), 500

    @app.route("/", methods=["GET"])
    def index():
        try:
            # Dynamically fetch simulation files from the simulations folder
            simulations_dir = os.path.join(os.path.dirname(__file__), "../simulations")
            simulation_files = [
                os.path.splitext(file)[0] for file in os.listdir(simulations_dir) if file.endswith(".py") and file != "__init__.py"
            ]
            simulations = [
                {"id": sim, "name": sim.replace("_", " ").title()} for sim in simulation_files
            ]
            # Pass datetime and timedelta to the template
            return render_template("index.html", simulations=simulations, datetime=datetime, timedelta=timedelta)
        except Exception as e:
            logging.error(f"Error in index: {e}")
            return jsonify({"error": str(e)}), 500
