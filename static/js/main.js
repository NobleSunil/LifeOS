document.addEventListener('DOMContentLoaded', () => {
    // Sidebar toggle logic
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const toggleBtn = document.getElementById('sidebarToggle');
    const closeBtn = document.getElementById('sidebarClose');

    const openSidebar = () => {
        if(sidebar) sidebar.classList.add('active');
        if(overlay) overlay.classList.add('active');
    };

    const closeSidebar = () => {
        if(sidebar) sidebar.classList.remove('active');
        if(overlay) overlay.classList.remove('active');
    };

    if(toggleBtn) toggleBtn.addEventListener('click', openSidebar);
    if(closeBtn) closeBtn.addEventListener('click', closeSidebar);
    if(overlay) overlay.addEventListener('click', closeSidebar);

    // Profile Dropdown logic
    const avatarBtn = document.getElementById('avatarBtn');
    const dropdown = document.getElementById('profileDropdown');

    if (avatarBtn && dropdown) {
        avatarBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('active');
        });
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target) && e.target !== avatarBtn) {
                dropdown.classList.remove('active');
            }
        });
    }

    // Floating Action Button Modal logic
    const modal = document.getElementById('fabModal');
    const fabBtn = document.getElementById('fabBtn');
    const closeFab = document.getElementById('closeFabModal');

    if(fabBtn && modal) {
        fabBtn.addEventListener('click', () => {
            modal.style.display = 'block';
        });
        if(closeFab) {
            closeFab.addEventListener('click', () => {
                modal.style.display = 'none';
            });
        }
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
});

// Appended UI Expand Logic

function toggleGoal(id) {
    const el = document.getElementById(`expand-${id}`);
    const toggle = document.getElementById(`toggle-${id}`);
    if(el && toggle) {
        if(el.style.display === 'none' || el.style.display === '') {
            el.style.display = 'block';
            toggle.style.transform = 'rotate(90deg)';
        } else {
            el.style.display = 'none';
            toggle.style.transform = 'rotate(0deg)';
        }
    }
}

function toggleHabit(id) {
    const el = document.getElementById(`expand-${id}`);
    const toggle = document.getElementById(`toggle-${id}`);
    if(el && toggle) {
        if(el.style.display === 'none' || el.style.display === '') {
            el.style.display = 'block';
            toggle.style.transform = 'rotate(90deg)';
        } else {
            el.style.display = 'none';
            toggle.style.transform = 'rotate(0deg)';
        }
    }
}

function updateHabitVal(id, val) {
    const el = document.getElementById(`hval-${id}`);
    if(el) el.innerText = val + '%';
}

function updateTaskVal(id, val) {
    const el = document.getElementById(`tval-${id}`);
    if(el) el.innerText = val + '%';
}

function toggleCompleted() {
    const list = document.getElementById('completedList');
    const icon = document.getElementById('completedIcon');
    const label = document.getElementById('completedTextLabel');
    if(list && icon && label) {
        if (list.style.display === 'none') {
            list.style.display = 'flex';
            icon.style.transform = 'rotate(90deg)';
            label.innerText = 'Hide';
        } else {
            list.style.display = 'none';
            icon.style.transform = 'rotate(0deg)';
            label.innerText = 'Show';
        }
    }
}
