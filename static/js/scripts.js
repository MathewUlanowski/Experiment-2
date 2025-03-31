// Set default values for the form fields
const today = new Date();
const firstOfThisMonth = new Date(today.getFullYear(), today.getMonth(), 1);
const threeYearsAgo = new Date(firstOfThisMonth);
threeYearsAgo.setFullYear(threeYearsAgo.getFullYear() - 3);

document.getElementById("start_date").value = threeYearsAgo.toISOString().split("T")[0];
document.getElementById("end_date").value = firstOfThisMonth.toISOString().split("T")[0];
document.getElementById("initial_investment").value = "0";
document.getElementById("monthly_investment").value = "500";

// Format input fields as money
function formatMoneyInput(input) {
    input.addEventListener("input", () => {
        const value = input.value.replace(/,/g, "");
        if (!isNaN(value)) {
            input.value = parseFloat(value).toLocaleString("en-US");
        }
    });
}
formatMoneyInput(document.getElementById("initial_investment"));
formatMoneyInput(document.getElementById("monthly_investment"));

// Show loading indicator during requests
async function handleRequest(url, method = "GET", data = null) {
    const loadingIndicator = document.getElementById("loading-indicator");
    loadingIndicator.style.display = "block";
    try {
        const response = await axios({ url, method, data });
        return response;
    } finally {
        loadingIndicator.style.display = "none";
    }
}

// Function to fetch and populate available simulations
async function fetchSimulations() {
    try {
        const response = await axios.get("/available_simulations");
        const simulations = response.data.simulations;

        const simulationsContainer = document.getElementById("simulations-container");
        simulationsContainer.innerHTML = ""; // Clear existing options

        simulations.forEach(({ id, name }) => {
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.name = "simulations";
            checkbox.value = id;
            checkbox.id = `simulation-${id}`;

            const label = document.createElement("label");
            label.htmlFor = `simulation-${id}`;
            label.textContent = name;

            const wrapper = document.createElement("div");
            wrapper.className = "form-check";
            wrapper.appendChild(checkbox);
            wrapper.appendChild(label);

            simulationsContainer.appendChild(wrapper);
        });
    } catch (error) {
        console.error("Error fetching simulations:", error);
        alert("Failed to load available simulations.");
    }
}

// Fetch simulations on page load
document.addEventListener("DOMContentLoaded", fetchSimulations);

document.getElementById("simulate-btn").addEventListener("click", async () => {
    const form = document.getElementById("simulation-form");
    const formData = new FormData(form);

    // Collect selected simulations
    const selectedSimulations = Array.from(
        document.querySelectorAll('input[name="simulations"]:checked')
    ).map((checkbox) => checkbox.value);
    if (selectedSimulations.length === 0) {
        alert("Please select at least one simulation to run.");
        return;
    }
    formData.append("simulations", selectedSimulations.join(","));

    // Collect selected tickers (optional)
    const selectedTickers = Array.from(selectedTickersContainer.children).map((bubble) => bubble.textContent.trim());
    if (selectedTickers.length > 0) {
        formData.append("tickers", selectedTickers.join(","));
    }

    const params = new URLSearchParams(formData);

    // Validate required fields
    const requiredFields = ["start_date", "end_date", "initial_investment", "monthly_investment"];
    for (const field of requiredFields) {
        if (!formData.get(field)) {
            alert(`Error: Missing required field: ${field}`);
            return;
        }
    }

    const graphDiv = document.getElementById("simulation-graph");
    const loadingIndicator = document.getElementById("loading-indicator");

    // Show loading indicator and clear the graph
    graphDiv.innerHTML = ""; // Clear any existing content
    loadingIndicator.style.display = "block";

    try {
        const response = await handleRequest(`/simulate?${params.toString()}`);
        const { data, layout } = response.data;

        if (!data || !layout) {
            throw new Error("Invalid response from the server.");
        }

        // Render the graph using Plotly's API
        Plotly.newPlot(graphDiv, data, layout);
    } catch (error) {
        alert("Error running simulation: " + (error.response?.data?.error || error.message));
    } finally {
        // Hide loading indicator
        loadingIndicator.style.display = "none";
    }
});

document.getElementById("clear-cache-btn").addEventListener("click", async () => {
    try {
        await handleRequest("/clear_cache", "POST");
        alert("Cache cleared successfully.");
    } catch (error) {
        alert("Error clearing cache: " + error.response.data.error);
    }
});

document.getElementById("delete-data-cache-btn").addEventListener("click", async () => {
    try {
        await handleRequest("/delete_data_cache", "POST");
        alert("Data cache deleted successfully.");
    } catch (error) {
        alert("Error deleting data cache: " + error.response.data.error);
    }
});

const tickerSearchInput = document.getElementById("ticker-search");
const tickerDropdown = document.getElementById("ticker-dropdown");
const selectedTickersContainer = document.getElementById("selected-tickers");
const selectedTickers = new Set();

let activeDropdownIndex = -1;

// Function to fetch and display ticker search results
tickerSearchInput.addEventListener("input", async () => {
    const query = tickerSearchInput.value.trim();
    if (!query) {
        tickerDropdown.style.display = "none";
        return;
    }

    try {
        const response = await axios.get(`/search_tickers?query=${query}`);
        const results = response.data.results;

        // Populate the dropdown with results
        tickerDropdown.innerHTML = "";
        results.forEach(({ symbol, name }, index) => {
            const listItem = document.createElement("li");
            listItem.className = "dropdown-item";
            listItem.innerHTML = `<strong>${symbol}</strong> - ${name}`;
            listItem.addEventListener("click", () => addTicker(symbol));
            listItem.setAttribute("data-index", index);
            tickerDropdown.appendChild(listItem);
        });

        activeDropdownIndex = -1; // Reset active index
        tickerDropdown.style.display = "block";
    } catch (error) {
        console.error("Error fetching tickers:", error);
    }
});

// Handle keyboard navigation for the dropdown
tickerSearchInput.addEventListener("keydown", (event) => {
    const items = tickerDropdown.querySelectorAll(".dropdown-item");
    if (items.length === 0) return;

    if (event.key === "ArrowDown") {
        // Move down in the dropdown
        event.preventDefault(); // Prevent default scrolling behavior
        if (activeDropdownIndex < items.length - 1) {
            activeDropdownIndex++;
            updateActiveDropdownItem(items);
        }
    } else if (event.key === "ArrowUp") {
        // Move up in the dropdown
        event.preventDefault(); // Prevent default scrolling behavior
        if (activeDropdownIndex > 0) {
            activeDropdownIndex--;
            updateActiveDropdownItem(items);
        }
    } else if (event.key === "Enter") {
        // Select the active item
        event.preventDefault(); // Prevent default behavior
        if (activeDropdownIndex >= 0 && activeDropdownIndex < items.length) {
            items[activeDropdownIndex].click();
        }
    }
});

// Function to update the active dropdown item
function updateActiveDropdownItem(items) {
    items.forEach((item, index) => {
        if (index === activeDropdownIndex) {
            item.classList.add("active");
            item.scrollIntoView({ block: "nearest" });
        } else {
            item.classList.remove("active");
        }
    });
}

// Function to add a ticker to the selected list
function addTicker(ticker) {
    if (selectedTickers.has(ticker)) return;

    selectedTickers.add(ticker);

    const bubble = document.createElement("span");
    bubble.className = "badge bg-primary text-white d-flex align-items-center gap-2";
    bubble.textContent = ticker;

    const removeButton = document.createElement("button");
    removeButton.className = "btn-close btn-close-white";
    removeButton.setAttribute("aria-label", "Remove");
    removeButton.addEventListener("click", () => {
        selectedTickers.delete(ticker);
        bubble.remove();
    });

    bubble.appendChild(removeButton);
    selectedTickersContainer.appendChild(bubble);

    tickerSearchInput.value = "";
    tickerDropdown.style.display = "none";
}

// Add default tickers on page load
document.addEventListener("DOMContentLoaded", () => {
    const defaultTickers = ["TSLA", "NVDA", "MSFT"];
    defaultTickers.forEach(addTicker);
});

// Hide dropdown when clicking outside
document.addEventListener("click", (event) => {
    if (!tickerSearchInput.contains(event.target) && !tickerDropdown.contains(event.target)) {
        tickerDropdown.style.display = "none";
    }
});
