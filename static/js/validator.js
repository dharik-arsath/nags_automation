function validatePieces(input) {
    // Convert input value to number
    let value = Number(input.value);
    
    // Ensure the value is within bounds
    if (value > 24) {
        input.value = 24;
    } else if (value < 0) {
        input.value = 0;
    }
    
    // Remove any decimal points
    input.value = Math.floor(input.value);
}