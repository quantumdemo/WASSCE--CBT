document.addEventListener('DOMContentLoaded', () => {
    const selectAllCheckbox = document.getElementById('select-all');
    const questionCheckboxes = document.querySelectorAll('.question-checkbox');
    const searchInput = document.getElementById('question-search');
    const questionsTable = document.getElementById('questions-table').querySelector('tbody');
    const tableRows = questionsTable.getElementsByTagName('tr');

    // 1. "Select All" functionality
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', (e) => {
            questionCheckboxes.forEach(checkbox => {
                checkbox.checked = e.target.checked;
            });
        });
    }

    // 2. Live search/filter functionality
    if (searchInput) {
        searchInput.addEventListener('keyup', () => {
            const filter = searchInput.value.toLowerCase();

            for (let i = 0; i < tableRows.length; i++) {
                const row = tableRows[i];
                const cells = row.getElementsByTagName('td');
                const questionText = cells[1].textContent || cells[1].innerText;
                const topicText = cells[2].textContent || cells[2].innerText;

                if (questionText.toLowerCase().indexOf(filter) > -1 || topicText.toLowerCase().indexOf(filter) > -1) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            }
        });
    }
});