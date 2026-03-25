document.addEventListener('DOMContentLoaded', () => {


    // --- 2. Filter Tabs Logic ---
    const filterTabs = document.querySelectorAll('.filter-tab');
    const goalCards = document.querySelectorAll('.goal-card');
    
    const activePlaceholder = document.getElementById('emptyActivePlaceholder');
    const completedPlaceholder = document.getElementById('emptyCompletedPlaceholder');
    const globalPlaceholder = document.getElementById('emptyGlobalPlaceholder');

    const evalEmptyStates = (filter) => {
        let visibleCount = 0;
        goalCards.forEach(c => {
            if(c.style.display !== 'none') visibleCount++;
        });

        if(globalPlaceholder) globalPlaceholder.style.display = 'none';
        if(activePlaceholder) activePlaceholder.style.display = 'none';
        if(completedPlaceholder) completedPlaceholder.style.display = 'none';

        if(visibleCount === 0) {
            if(filter === 'All' && globalPlaceholder) globalPlaceholder.style.display = 'block';
            if(filter === 'Active' && activePlaceholder) activePlaceholder.style.display = 'block';
            if(filter === 'Completed' && completedPlaceholder) completedPlaceholder.style.display = 'block';
        }
    };

    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Reset active tabs
            filterTabs.forEach(t => {
                t.classList.remove('active');
                t.style.borderBottom = 'none';
                t.style.fontWeight = '500';
                t.style.color = 'var(--text-secondary)';
            });
            // Activate current tab
            tab.classList.add('active');
            tab.style.borderBottom = '2px solid var(--primary-color)';
            tab.style.fontWeight = '600';
            tab.style.color = 'var(--primary-color)';

            const filter = tab.getAttribute('data-filter');

            goalCards.forEach(card => {
                if (filter === 'All') {
                    card.style.display = 'block';
                } else if (filter === 'Active') {
                    card.style.display = card.getAttribute('data-status') === 'Active' ? 'block' : 'none';
                } else if (filter === 'Completed') {
                    card.style.display = card.getAttribute('data-status') === 'Completed' ? 'block' : 'none';
                }
            });
            
            evalEmptyStates(filter);
        });
    });

    // --- 3. Modal Forms (+ New / Edit) ---
    const goalModal = document.getElementById('goalModal');
    const newGoalBtn = document.getElementById('newGoalBtn');
    const closeGoalModal = document.getElementById('closeGoalModal');
    
    // Explicit Base URL mapping assuming `/goals/` handles creation
    const goalForm = document.getElementById('goalForm');
    const baseActionUrl = goalForm ? goalForm.action : ''; 

    if (newGoalBtn) {
        newGoalBtn.addEventListener('click', () => {
            document.getElementById('goalModalTitle').innerText = 'New Goal';
            document.getElementById('goalTitleInput').value = '';
            document.getElementById('goalDescInput').value = '';
            document.getElementById('goalStatusInput').value = 'Active';
            document.getElementById('goalForm').action = baseActionUrl; // reset to base
            
            // Allow goal type selection 
            document.getElementById('type_task').checked = true;
            document.getElementById('targetDaysGroup').style.display = 'none';
            document.getElementById('targetDaysInput').value = '';
            document.getElementById('targetDaysInput').required = false;
            document.getElementById('goalTypeReadonlyNote').style.display = 'none';
            document.querySelectorAll('input[name="goal_type"]').forEach(r => r.disabled = false);

            goalModal.style.display = 'block';
        });
    }

    if (closeGoalModal) {
        closeGoalModal.addEventListener('click', () => {
            goalModal.style.display = 'none';
        });
    }

    document.querySelectorAll('.edit-goal-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation(); // prevent row collapse toggle
            
            const id = btn.getAttribute('data-id');
            const title = btn.getAttribute('data-title');
            const desc = btn.getAttribute('data-desc');
            const status = btn.getAttribute('data-status');
            const type = btn.getAttribute('data-type');
            const target = btn.getAttribute('data-target');
            
            document.getElementById('goalModalTitle').innerText = 'Edit Goal';
            document.getElementById('goalTitleInput').value = title;
            document.getElementById('goalDescInput').value = desc;
            document.getElementById('goalStatusInput').value = status;
            
            if (type === 'habit_based') {
                document.getElementById('type_habit').checked = true;
                document.getElementById('targetDaysGroup').style.display = 'block';
                document.getElementById('targetDaysInput').value = target || '';
                document.getElementById('targetDaysInput').required = true;
            } else {
                document.getElementById('type_task').checked = true;
                document.getElementById('targetDaysGroup').style.display = 'none';
                document.getElementById('targetDaysInput').value = '';
                document.getElementById('targetDaysInput').required = false;
            }

            // Readonly for edits
            document.querySelectorAll('input[name="goal_type"]').forEach(r => r.disabled = true);
            document.getElementById('goalTypeReadonlyNote').style.display = 'block';
            
            document.getElementById('goalForm').action = `/goals/${id}/edit/`;
            goalModal.style.display = 'block';
        });
    });

    // Modal Background Close
    window.addEventListener('click', (e) => {
        if(e.target === goalModal) goalModal.style.display = 'none';
        
        const autoModal = document.getElementById('autoCompleteModal');
        if(e.target === autoModal) autoModal.style.display = 'none';
    });

    // Toggle event listener for radio buttons
    document.querySelectorAll('input[name="goal_type"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'habit_based') {
                document.getElementById('targetDaysGroup').style.display = 'block';
                document.getElementById('targetDaysInput').required = true;
            } else {
                document.getElementById('targetDaysGroup').style.display = 'none';
                document.getElementById('targetDaysInput').required = false;
                document.getElementById('targetDaysInput').value = '';
            }
        });
    });

    // --- 4. Auto-Complete Logic Check ---
    const autoModal = document.getElementById('autoCompleteModal');
    const closeAuto = document.getElementById('closeAutoComplete');
    
    if (closeAuto) {
        closeAuto.addEventListener('click', () => {
            autoModal.style.display = 'none';
        });
    }

    // Check if any Active goal just hit 100%
    let triggeredAuto = false;
    goalCards.forEach(card => {
        if(triggeredAuto) return; // Only prompt once per load
        const status = card.getAttribute('data-status');
        const progress = card.getAttribute('data-progress');
        
        if (status === 'Active' && progress === '100') {
            const title = card.querySelector('.goal-header h4').innerText.replace('🎯 ', '');
            const goalId = card.querySelector('.edit-goal-btn').getAttribute('data-id');
            
            document.getElementById('autoCompleteGoalTitle').innerText = title;
            document.getElementById('autoCompleteForm').action = `/goals/${goalId}/complete/`;
            
            autoModal.style.display = 'block';
            triggeredAuto = true;
        }
    });

});
