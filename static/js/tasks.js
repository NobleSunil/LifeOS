// Task slider live value update (global — called from oninput in template)
function updateSliderValue(taskId, value) {
    const el = document.getElementById('val_' + taskId);
    if (el) el.textContent = value + '%';
}

document.addEventListener('DOMContentLoaded', () => {

    // --- 1. Filter Logic ---
    const filterTabs = document.querySelectorAll('.filter-tab');
    const goalSelect = document.getElementById('filterGoalSelect');
    
    const taskCards = document.querySelectorAll('.task-card');
    const sections = document.querySelectorAll('.task-section');
    const emptyFilterPlaceholder = document.getElementById('emptyFilterPlaceholder');
    const emptyGlobalPlaceholder = document.getElementById('emptyGlobalPlaceholder');

    const updateVisibility = (filterType, filterValue) => {
        let totalVisible = 0;
        
        taskCards.forEach(card => {
            let show = false;
            
            if (filterType === 'Tab') {
                if (filterValue === 'All') show = true;
                else if (filterValue === 'Today') show = card.getAttribute('data-is-today') === 'true';
                else if (filterValue === 'Overdue') show = card.getAttribute('data-is-overdue') === 'true';
            } 
            else if (filterType === 'Goal') {
                show = card.getAttribute('data-goal-id') === filterValue;
            }

            card.style.display = show ? 'flex' : 'none';
        });

        // Evaluate Sections
        sections.forEach(sec => {
            // Get task cards in this section and check which are visible
            const sectionCards = Array.from(sec.querySelectorAll('.task-card'));
            const visibleCards = sectionCards.filter(c => c.style.display !== 'none');
            const emptyMsg = sec.querySelector('.empty-section-msg');
            
            if (visibleCards.length === 0) {
                if (emptyMsg && filterType === 'Tab' && filterValue === 'All') {
                    // Native empty state for Pending/Completed
                    sec.style.display = 'block';
                    emptyMsg.style.display = 'block';
                    totalVisible++;
                } else {
                    sec.style.display = 'none';
                }
            } else {
                sec.style.display = 'block';
                if (emptyMsg) emptyMsg.style.display = 'none';
                totalVisible += visibleCards.length;
            }
        });

        if (emptyFilterPlaceholder) {
            emptyFilterPlaceholder.style.display = (totalVisible === 0 && !emptyGlobalPlaceholder) ? 'block' : 'none';
        }
    };

    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Reset Tabs UI
            filterTabs.forEach(t => {
                t.classList.remove('active');
                t.style.borderBottom = 'none';
                t.style.fontWeight = '500';
                t.style.color = 'var(--text-secondary)';
            });
            tab.classList.add('active');
            tab.style.borderBottom = '2px solid var(--primary-color)';
            tab.style.fontWeight = '600';
            tab.style.color = 'var(--primary-color)';

            // Reset Selects
            if(goalSelect) goalSelect.value = '';

            updateVisibility('Tab', tab.getAttribute('data-filter'));
        });
    });

    if(goalSelect) {
        goalSelect.addEventListener('change', (e) => {
            if(e.target.value === '') return;
            filterTabs.forEach(t => {
                t.classList.remove('active');
                t.style.borderBottom = 'none';
                t.style.fontWeight = '500';
                t.style.color = 'var(--text-secondary)';
            });
            updateVisibility('Goal', e.target.value);
        });
    }

    // --- 2. Completed Section Toggle ---
    const completedToggle = document.getElementById('completedToggle');
    const completedList = document.getElementById('completedList');
    const completedIcon = document.getElementById('completedIcon');
    const completedTextLabel = document.getElementById('completedTextLabel');

    if (completedToggle && completedList) {
        completedToggle.addEventListener('click', () => {
            if (completedList.style.display === 'none') {
                completedList.style.display = 'flex';
                completedIcon.style.transform = 'rotate(90deg)';
                completedTextLabel.innerText = 'Hide';
            } else {
                completedList.style.display = 'none';
                completedIcon.style.transform = 'rotate(0deg)';
                completedTextLabel.innerText = 'Show';
            }
        });
    }

    // --- 3. Modals & Form Validation ---
    const taskModal = document.getElementById('taskModal');
    const newTaskBtn = document.getElementById('newTaskBtn');
    const closeTaskModal = document.getElementById('closeTaskModal');
    const taskForm = document.getElementById('taskForm');
    const baseActionUrl = taskForm ? taskForm.action : '';
    const dateError = document.getElementById('dateError');

    const resetForm = () => {
        document.getElementById('taskModalTitle').innerText = 'New Task';
        document.getElementById('taskTitleInput').value = '';
        document.getElementById('taskDescInput').value = '';
        document.getElementById('taskStartInput').value = '';
        document.getElementById('taskDueInput').value = '';
        document.getElementById('taskGoalInput').value = '';
        document.getElementById('taskStatusInput').value = 'Pending';
        // Reset task type to simple
        const simpleRadio = document.getElementById('type_simple');
        if (simpleRadio) simpleRadio.checked = true;
        // Re-enable radios (may have been disabled for edit)
        document.querySelectorAll('#taskForm input[name="task_type"]').forEach(r => r.disabled = false);
        if (taskForm) taskForm.action = baseActionUrl;
        if (dateError) dateError.style.display = 'none';
    };

    if (newTaskBtn) {
        newTaskBtn.addEventListener('click', () => {
            resetForm();
            taskModal.style.display = 'block';
        });
    }

    if (closeTaskModal) {
        closeTaskModal.addEventListener('click', () => {
            taskModal.style.display = 'none';
        });
    }

    document.querySelectorAll('.edit-task-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            resetForm();
            document.getElementById('taskModalTitle').innerText = 'Edit Task';
            
            document.getElementById('taskTitleInput').value = btn.getAttribute('data-title');
            document.getElementById('taskDescInput').value = btn.getAttribute('data-desc');
            document.getElementById('taskStartInput').value = btn.getAttribute('data-start');
            document.getElementById('taskDueInput').value = btn.getAttribute('data-due');
            document.getElementById('taskGoalInput').value = btn.getAttribute('data-goal');
            document.getElementById('taskStatusInput').value = btn.getAttribute('data-status');

            // Set task_type radio and lock it (cannot change after creation)
            const taskType = btn.getAttribute('data-task-type') || 'simple';
            document.querySelectorAll('#taskForm input[name="task_type"]').forEach(r => {
                r.checked = (r.value === taskType);
                r.disabled = true;  // lock on edit
            });
            
            taskForm.action = `/tasks/${btn.getAttribute('data-id')}/edit/`;
            taskModal.style.display = 'block';
        });
    });

    if (taskForm) {
        taskForm.addEventListener('submit', (e) => {
            const start = document.getElementById('taskStartInput').value;
            const due = document.getElementById('taskDueInput').value;
            if (start && due) {
                if (new Date(due) < new Date(start)) {
                    e.preventDefault();
                    if (dateError) dateError.style.display = 'block';
                }
            }
        });
    }

    // Modal Background Close
    window.addEventListener('click', (e) => {
        if(e.target === taskModal) taskModal.style.display = 'none';
        const autoModal = document.getElementById('autoCompleteGoalModal');
        if(e.target === autoModal) autoModal.style.display = 'none';
    });

    // --- 4. Auto Complete Goal Triggers ---
    let autoTriggered = false;
    window.triggerAutoCompleteGoal = (goalId, goalTitle) => {
        if(autoTriggered) return;
        
        const autoModal = document.getElementById('autoCompleteGoalModal');
        document.getElementById('autoCompleteGoalName').innerText = goalTitle;
        document.getElementById('autoCompleteGoalForm').action = `/goals/${goalId}/complete/`;
        
        if (autoModal) autoModal.style.display = 'block';
        autoTriggered = true;
    };

    const closeAutoGoalModal = document.getElementById('closeAutoCompleteGoal');
    if (closeAutoGoalModal) {
        closeAutoGoalModal.addEventListener('click', () => {
            document.getElementById('autoCompleteGoalModal').style.display = 'none';
        });
    }

});
