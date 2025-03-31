import plotly.graph_objs as go

def generate_plot(balance_histories):
    """
    Generates a Plotly graph from a list of balance histories.

    :param balance_histories: A list of tuples, where each tuple contains an account name and its balance history.
                              Each balance history is a list of dictionaries with a 'date', 'account_balance', and other properties.
    :return: A Plotly figure object.
    """
    fig = go.Figure()

    for account_name, balance_history in balance_histories:
        if not balance_history:
            continue

        # Extract dates and account balances
        dates = [entry["date"] for entry in balance_history]
        account_balances = [entry["account_balance"] for entry in balance_history]

        # Dynamically generate hover template with additional properties
        hovertemplate = "<b>Date:</b> %{x}<br><b>Account Balance:</b> $%{y:,.2f}<br>"
        customdata = []

        for key in balance_history[0].keys():
            if key not in ["date", "account_balance"]:
                hovertemplate += f"<b>{key.replace('_', ' ').title()}:</b> %{{customdata[{len(customdata)}]}}<br>"
                customdata.append([entry[key] for entry in balance_history])

        hovertemplate += "<extra></extra>"  # Remove extra hover info

        # Transpose customdata to match Plotly's format
        customdata = list(zip(*customdata))

        # Add trace for account balance
        fig.add_trace(go.Scatter(
            x=dates,
            y=account_balances,
            mode="lines",
            name=account_name,
            hovertemplate=hovertemplate,
            customdata=customdata
        ))

    # Update layout
    fig.update_layout(
        title="Simulation Results",
        xaxis_title="Date",
        yaxis=dict(
            title="Account Balance",
            tickformat="$,.2f"  # Format Y-axis as money
        ),
        template="plotly_dark",
        font=dict(color="white"),
        paper_bgcolor="#121212",
        plot_bgcolor="#121212"
    )

    return fig
