document.addEventListener('DOMContentLoaded', () => {
    const calDays = document.querySelectorAll('.active-day');
    
    const todayFormContainer = document.getElementById('todayFormContainer');
    const todayFormHeader = document.getElementById('todayFormHeader');
    const readOnlyContainer = document.getElementById('readOnlyContainer');
    
    // Form Inputs
    const winsInput = document.getElementById('winsInput');
    const challengesInput = document.getElementById('challengesInput');
    const tomorrowInput = document.getElementById('tomorrowInput');
    const reflectionForm = todayFormContainer ? todayFormContainer.querySelector('form') : null;
    
    // Original Action URL for Today Form
    const baseActionUrl = reflectionForm ? reflectionForm.action : '';

    // ReadOnly Fields
    const readOnlyHeader = document.getElementById('readOnlyHeader');
    const readOnlyWins = document.getElementById('readOnlyWins');
    const readOnlyChallenges = document.getElementById('readOnlyChallenges');
    const readOnlyTomorrow = document.getElementById('readOnlyTomorrow');
    
    // Actions
    const editPastBtn = document.getElementById('editPastBtn');
    const deleteReflectionForm = document.getElementById('deleteReflectionForm');
    
    // Current viewed past target
    let currentPastId = null;
    let currentPastDateStr = null;

    // Date formatting helper
    function formatDateStr(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr + "T00:00:00"); 
        return d.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
    }

    // Set form wrapper to edit today
    function loadTodayForm() {
        if (!todayFormContainer || !readOnlyContainer) return;

        readOnlyContainer.style.display = 'none';
        todayFormContainer.style.display = 'block';
        
        if(window.todayDateStr) {
            todayFormHeader.innerHTML = `📝 Today's Reflection <span style="font-weight:400; font-size:1rem; color:var(--text-secondary); margin-left:10px;">— ${formatDateStr(window.todayDateStr)}</span>`;
        }
        
        reflectionForm.action = baseActionUrl;
        
        if (window.reflectionsData && window.reflectionsData[window.todayDateStr]) {
            const data = window.reflectionsData[window.todayDateStr];
            winsInput.value = data.wins || '';
            challengesInput.value = data.challenges || '';
            tomorrowInput.value = data.tomorrow || '';
            document.getElementById('saveReflectionBtn').innerText = 'Update Reflection';
        } else if (winsInput) {
            winsInput.value = '';
            challengesInput.value = '';
            tomorrowInput.value = '';
            document.getElementById('saveReflectionBtn').innerText = 'Save Reflection';
        }
    }
    
    // Initialize standard view parsing existing today dict implicitly.
    loadTodayForm();
    
    // Interaction Handlers mapping click routines dynamically
    calDays.forEach(day => {
        day.addEventListener('click', () => {
            const dateStr = day.getAttribute('data-date');
            const isToday = day.getAttribute('data-today') === 'true';
            
            if (isToday) {
                loadTodayForm();
            } else if (window.reflectionsData[dateStr]) {
                const data = window.reflectionsData[dateStr];
                currentPastId = data.id;
                currentPastDateStr = dateStr;
                
                todayFormContainer.style.display = 'none';
                readOnlyContainer.style.display = 'block';
                
                readOnlyHeader.innerHTML = `📅 Reflection from <span style="font-weight:400; font-size:1rem; color:var(--text-secondary); margin-left:10px;">${formatDateStr(dateStr)}</span>`;
                
                readOnlyWins.innerText = data.wins || '—';
                readOnlyChallenges.innerText = data.challenges || '—';
                readOnlyTomorrow.innerText = data.tomorrow || '—';
                
                deleteReflectionForm.action = `/reflections/delete/${data.id}/`;
            }
        });
    });
    
    // Edit Past Button -> loads the target's fields into the standard form mapped securely
    if(editPastBtn) {
        editPastBtn.addEventListener('click', () => {
            if(!currentPastId) return;
            const data = window.reflectionsData[currentPastDateStr];
            
            readOnlyContainer.style.display = 'none';
            todayFormContainer.style.display = 'block';
            
            todayFormHeader.innerHTML = `✏️ Editing Reflection <span style="font-weight:400; font-size:1rem; color:var(--text-secondary); margin-left:10px;">— ${formatDateStr(currentPastDateStr)}</span>`;
            
            winsInput.value = data.wins || '';
            challengesInput.value = data.challenges || '';
            tomorrowInput.value = data.tomorrow || '';
            
            document.getElementById('saveReflectionBtn').innerText = 'Save Changes';
            reflectionForm.action = `/reflections/edit/${currentPastId}/`;
        });
    }

    // Form Validation checking for completely empty subsets
    window.validateReflectionForm = function() {
        if (!winsInput || !challengesInput || !tomorrowInput) return true;
        if (!winsInput.value.trim() && !challengesInput.value.trim() && !tomorrowInput.value.trim()) {
            document.getElementById('formErrorMsg').style.display = 'block';
            return false;
        }
        document.getElementById('formErrorMsg').style.display = 'none';
        return true;
    };
});
