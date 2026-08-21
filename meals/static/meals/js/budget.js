// Find budget elements on the page
const budgetInput = document.getElementById("weekly-budget");
const budgetSlider = document.getElementById("budget-slider");
const dailyBudget = document.getElementById("daily-budget");

// Calculate and display daily budget
function updateDailyBudget(weeklyAmount) {
    // Convert input from text into number
    const weeklyBudget = Number(weeklyAmount);

    // Prevemt invalid or negative values
    if (weeklyBudget <= 0 || Number.isNaN(weeklyBudget)) {
        dailyBudget.textContent = "£0.00";
        return;
    }

    // Divide weekly amount across seven days
    const dailyAmount = weeklyBudget / 7;

    // Display the result as a currency with two decimal places
    dailyBudget.textContent = `£${dailyAmount.toFixed(2)}`;
}

// Update the result when the number input changes
budgetInput.addEventListener("input", function() {
    const value = budgetInput.value;

    // Keep slider matched when value is within its range
    if (value >=5 && value <= 100) {
        budgetSlider.value = value;
    }

    updateDailyBudget(value);
});

// Update the number input when the slider changes
budgetSlider.addEventListener("input", function () {
    budgetInput.value = budgetSlider.value;
    updateDailyBudget(budgetSlider.value);
})

// Display corect daily amount when page first loads
updateDailyBudget(budgetInput.value);