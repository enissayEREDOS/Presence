document.getElementById('menu-btn').addEventListener('click', function() {
    document.getElementById('sidebar').classList.toggle('hidden');
    document.getElementById('main-content').classList.toggle('full-width');
});


document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    sidebar.style.scrollBehavior = 'smooth'; // Active le défilement fluide

    // Gestion des sous-menus (comme dans la réponse précédente)
    const menuItems = document.querySelectorAll('.sidebar ul li a');

    menuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            const parentLi = this.parentNode;
            const submenu = parentLi.querySelector('.submenu');

            if (submenu) {
                e.preventDefault();
                parentLi.classList.toggle('active');
            }
        });
    });
});


