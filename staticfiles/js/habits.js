document.addEventListener('DOMContentLoaded', () => {

    // --- 1. Inline Expand Toggle ---
    const headers = document.querySelectorAll('.habit-header');
    
    headers.forEach(header => {
        header.addEventListener('click', (e) => {
            const habitId = header.getAttribute('data-id');
            const details = document.getElementById(`details-${habitId}`);
            const icon = document.getElementById(`icon-${habitId}`);
            
            if (details.style.display === 'none') {
                details.style.display = 'block';
                icon.style.transform = 'rotate(90deg)';
                header.style.backgroundColor = '#f8fafc';
            } else {
                details.style.display = 'none';
                icon.style.transform = 'rotate(0deg)';
                header.style.backgroundColor = 'transparent';
            }
        });
    });

    // --- 2. Habit Slider Live Update ---
    window.updateHabitSlider = function(habitId, value) {
        const el = document.getElementById('hval_' + habitId);
        if (el) el.innerText = value + '%';
    };

    // --- 3. Modals & Form Logic ---
    const habitModal = document.getElementById('habitModal');
    const newHabitBtn = document.getElementById('newHabitBtn');
    const closeHabitModal = document.getElementById('closeHabitModal');
    const habitForm = document.getElementById('habitForm');
    const baseActionUrl = habitForm ? habitForm.action : '';
    const trackingModeReadonlyNote = document.getElementById('trackingModeReadonlyNote');

    const resetForm = () => {
        document.getElementById('habitModalTitle').innerText = 'New Habit';
        document.getElementById('habitNameInput').value = '';
        document.getElementById('habitGoalInput').value = '';
        if (habitForm) habitForm.action = baseActionUrl;

        // Reset tracking mode radio to default (manual_slider)
        const sliderRadio = document.getElementById('mode_slider');
        if (sliderRadio) sliderRadio.checked = true;

        // Enable all radios (for new habit)
        document.querySelectorAll('#habitForm input[name="tracking_mode"]').forEach(r => {
            r.disabled = false;
        });
        if (trackingModeReadonlyNote) trackingModeReadonlyNote.style.display = 'none';
    };

    if (newHabitBtn) {
        newHabitBtn.addEventListener('click', () => {
            resetForm();
            habitModal.style.display = 'block';
        });
    }

    if (closeHabitModal) {
        closeHabitModal.addEventListener('click', () => {
            habitModal.style.display = 'none';
        });
    }

    document.querySelectorAll('.edit-habit-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            resetForm();
            document.getElementById('habitModalTitle').innerText = 'Edit Habit';
            
            document.getElementById('habitNameInput').value = btn.getAttribute('data-name');
            document.getElementById('habitGoalInput').value = btn.getAttribute('data-goal');

            // Set & lock tracking mode (cannot be changed after creation)
            const mode = btn.getAttribute('data-tracking-mode') || 'manual_slider';
            document.querySelectorAll('#habitForm input[name="tracking_mode"]').forEach(r => {
                r.checked = (r.value === mode);
                r.disabled = true;  // lock all radios on edit
            });
            if (trackingModeReadonlyNote) trackingModeReadonlyNote.style.display = 'block';
            
            if (habitForm) habitForm.action = `/habits/edit/${btn.getAttribute('data-id')}/`;
            if (habitModal) habitModal.style.display = 'block';
        });
    });

    // Modal Background Close
    window.addEventListener('click', (e) => {
        if(e.target === habitModal) habitModal.style.display = 'none';
    });
});
