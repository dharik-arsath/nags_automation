const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === "127.0.0.1";
const baseUrl = isDevelopment ? 'http://localhost:8000/' : 'https://nagaraj1.pythonanywhere.com/';


let driverListInfo = [];

async function fetchDrivers() {
    try {
        const response = await fetch(baseUrl + 'get_drivers');
        const drivers = await response.json();
        
        driverListInfo = drivers.map(driver => ({
            name: driver
        }));
    } catch (error) {
        console.error('Failed to fetch drivers:', error);
    }
}

// Call fetchDrivers when the script loads
fetchDrivers();
let lineListInfo = [];

async function fetchLines() {
    try {
        const response = await fetch(baseUrl + 'get_line');
        const lines = await response.json();
        
        lineListInfo = lines.map(line => ({
            line: line
        }));
    } catch (error) {
        console.error('Failed to fetch lines:', error);
    }
}

// Call fetchLines when the script loads
fetchLines();


let expensesListInfo = [];

async function fetchExpenses() {
    try {
        const response = await fetch(baseUrl + 'get_all_expenses');
        const expenses = await response.json();
        
        expensesListInfo = expenses.map(expense => ({
            expense: expense
        }));
    } catch (error) {
        console.error('Failed to fetch expenses:', error);
    }
}

// Call fetchExpenses when the script loads
fetchExpenses();



driverListInfo = driverListInfo.map(driver => ({
    ...driver,  // Keep the rest of the properties intact
    name: driver.name.toLowerCase()  // Convert the name to lowercase
}));


let productsV1 = [];

// Function to fetch products from the server
async function fetchProducts() {
    try {
        const response = await fetch(baseUrl + 'get_raw_data');
        if (!response.ok) {
            throw new Error('Failed to fetch products');
        }
        productsV1 = await response.json();
        return productsV1;
    } catch (error) {
        console.error('Error fetching products:', error);
        return [];
    }
}

// Function to get a specific product by name
function getProductByName(productName) {
    return productsV1.find(product => 
        product.name.toLowerCase() === productName.toLowerCase()
    );
}

// Fetch products when the script loads
fetchProducts();



// Add at the top of your file
let cachedExpenseOptions = null;

async function loadExpenseOptions() {
    if (cachedExpenseOptions) {
        return cachedExpenseOptions;
    }
    
    try {
        const response = await fetch(baseUrl + 'get_all_expenses');
        if (!response.ok) throw new Error('Failed to load expense options');
        cachedExpenseOptions = await response.json();
        return cachedExpenseOptions;
    } catch (error) {
        console.error('Error loading expense options:', error);
        return [];
    }
}