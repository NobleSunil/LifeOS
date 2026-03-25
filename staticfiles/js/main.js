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
