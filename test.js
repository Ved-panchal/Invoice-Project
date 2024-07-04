function simulateSearchInput(value) {
    // Get the input element
    const searchInput = document.querySelector("#searchInputContainer_search1 > div > input")

    // Set the value of the input element
    searchInput.value = value;

    // Create and dispatch an 'input' event
    const inputEvent = new Event('input', {
        bubbles: true,
        cancelable: true
    });
    searchInput.dispatchEvent(inputEvent);

    const enterKeyEvent = new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        key: 'Enter',
        code: 'Enter',
        keyCode: 13, // Deprecated but included for compatibility
        which: 13
    });
    searchInput.dispatchEvent(enterKeyEvent);
}

// document.getElementById('searchInput').addEventListener('change', (e) => {
//     console.log('Change event triggered');
//     console.log('New value: ', e.target.value);
// });

// document.getElementById('searchInput').addEventListener('input', (e) => {
//     console.log('Input event triggered');
//     console.log('New value: ', e.target.value);
// });

// document.getElementById('searchInput').addEventListener('keydown', (e) => {
//     if (e.key === 'Enter') {
//         console.log('Enter key pressed');
//         // Simulate a form submit or search action
//     }
// });
