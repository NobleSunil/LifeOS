document.addEventListener('DOMContentLoaded', () => {
    const fromInput = document.getElementById('reportFromDate');
    const toInput = document.getElementById('reportToDate');
    const checkboxes = document.querySelectorAll('.report-checkbox');
    const downloadBtn = document.getElementById('downloadBtn');
    
    const sumTasks = document.getElementById('sumTasks');
    const sumHabits = document.getElementById('sumHabits');
    const sumGoals = document.getElementById('sumGoals');
    const sumReflections = document.getElementById('sumReflections');
    const sumTotal = document.getElementById('sumTotal');
    
    const dateErrorMsg = document.getElementById('dateErrorMsg');
    const checkboxErrorMsg = document.getElementById('checkboxErrorMsg');
    const emptyDataMsg = document.getElementById('emptyDataMsg');
    
    const downloadForm = document.getElementById('downloadForm');
    const hiddenFromDate = document.getElementById('hiddenFromDate');
    const hiddenToDate = document.getElementById('hiddenToDate');

    // Initialize dates -> default to Last 30 days or min_date if newer
    let defaultFromDate = new Date();
    defaultFromDate.setDate(defaultFromDate.getDate() - 30);
    const minD = new Date(window.reportsMinDate + "T00:00:00");
    if (defaultFromDate < minD) defaultFromDate = minD;
    
    fromInput.value = defaultFromDate.toISOString().split('T')[0];
    toInput.value = window.reportsMaxDate;

    // Wait until they stop typing to fetch
    let fetchTimeout;

    function formatValue(val) {
        if (val === 0) {
            return '<span style="color:#94a3b8; font-weight:400;">No data</span>';
        }
        return val;
    }

    function checkValidityAndFetch() {
        const fromDateStr = fromInput.value;
        const toDateStr = toInput.value;
        
        dateErrorMsg.style.display = 'none';
        checkboxErrorMsg.style.display = 'none';
        emptyDataMsg.style.display = 'none';
        
        let isValid = true;
        
        if (!fromDateStr || !toDateStr) {
            isValid = false;
        } else if (fromDateStr > toDateStr) {
            dateErrorMsg.innerText = 'From date cannot be after To date';
            dateErrorMsg.style.display = 'block';
            isValid = false;
        } else if (fromDateStr < window.reportsMinDate) {
            dateErrorMsg.innerText = 'Cannot select dates before your registration date';
            dateErrorMsg.style.display = 'block';
            isValid = false;
        } else if (toDateStr > window.reportsMaxDate) {
            dateErrorMsg.innerText = 'Cannot select future dates';
            dateErrorMsg.style.display = 'block';
            isValid = false;
        }

        let isChecked = false;
        checkboxes.forEach(cb => {
            if (cb.checked) isChecked = true;
        });

        if (!isChecked) {
            checkboxErrorMsg.style.display = 'block';
            isValid = false;
        }

        if (!isValid) {
            downloadBtn.disabled = true;
            sumTasks.innerHTML = '...';
            sumHabits.innerHTML = '...';
            sumGoals.innerHTML = '...';
            sumReflections.innerHTML = '...';
            sumTotal.innerHTML = '...';
            return;
        }

        clearTimeout(fetchTimeout);
        fetchTimeout = setTimeout(() => {
            fetchSummary(fromDateStr, toDateStr);
        }, 300);
    }

    function fetchSummary(f, t) {
        fetch(`/reports/summary/?from_date=${f}&to_date=${t}`)
            .then(res => res.json())
            .then(data => {
                if(data.error) {
                    dateErrorMsg.innerText = data.error;
                    dateErrorMsg.style.display = 'block';
                    downloadBtn.disabled = true;
                    return;
                }

                sumTasks.innerHTML = formatValue(data.tasks);
                sumHabits.innerHTML = formatValue(data.habits);
                sumGoals.innerHTML = formatValue(data.goals);
                sumReflections.innerHTML = formatValue(data.reflections);
                sumTotal.innerHTML = data.total;

                if (data.total === 0) {
                    emptyDataMsg.style.display = 'block';
                    downloadBtn.disabled = true;
                } else {
                    downloadBtn.disabled = false;
                }
            })
            .catch(err => {
                console.error("Error fetching summary:", err);
            });
    }

    // Bind listeners
    fromInput.addEventListener('change', checkValidityAndFetch);
    toInput.addEventListener('change', checkValidityAndFetch);
    
    checkboxes.forEach(cb => {
        cb.addEventListener('change', checkValidityAndFetch);
    });

    // Form onSubmit maps invisible inputs
    downloadForm.addEventListener('submit', (e) => {
        hiddenFromDate.value = fromInput.value;
        hiddenToDate.value = toInput.value;
        
        // Dynamic include inputs
        document.querySelectorAll('.dynamic-include').forEach(el => el.remove());
        
        checkboxes.forEach(cb => {
            if (cb.checked) {
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'include';
                hiddenInput.value = cb.value;
                hiddenInput.className = 'dynamic-include';
                downloadForm.appendChild(hiddenInput);
            }
        });
    });

    // Initial Trigger
    checkValidityAndFetch();
});
