function toggleDropdown() {
    const dropdown = document.getElementById('dropdown');
    dropdown.style.display = (dropdown.style.display === 'block') ? 'none' : 'block';
}

function toggleColumn(colIndex) {
    const table = document.querySelector('table');
    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('th, td');
        if (cells[colIndex]) {
            cells[colIndex].style.display = (cells[colIndex].style.display === 'none') ? '' : 'none';
        }
    });
}

document.addEventListener('click', function (event) {
    const dropdown = document.getElementById('dropdown');
    const button = document.querySelector('.options-button');
    if (!dropdown.contains(event.target) && !button.contains(event.target)) {
        dropdown.style.display = 'none';
    }
});