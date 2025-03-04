/**
 * Popup Menu Component
 * Handles the dropdown menu functionality
 */
class PopupMenu {
    constructor() {
        this.menuToggle = document.getElementById('menuToggle');
        this.popupMenu = document.getElementById('popupMenu');

        if (!this.menuToggle || !this.popupMenu) return;

        this.options = [
            {icon: 'fa-solid fa-house', text: 'Home', color: 'font-medium'},
            {icon: 'fa-solid fa-gear', text: 'Settings'},
            {icon: 'fa-solid fa-right-from-bracket', text: 'Close', color: 'text-red-500'}
        ];

        this.generateMenuItems();
        this.setupEventListeners();
    }

    generateMenuItems() {
        this.popupMenu.innerHTML = '';

        this.options.forEach((option, index) => {
            const isLast = index === this.options.length - 1;
            const menuItem = document.createElement('div');

            menuItem.className = `menu-item ${!isLast ? 'border-b menu-item-border' : ''} ${option.color || ''}`;
            menuItem.innerHTML = `<i class="${option.icon} mr-2"></i> ${option.text}`;

            this.popupMenu.appendChild(menuItem);

            // Optional: Add click event for each menu item
            menuItem.addEventListener('click', () => {
                this.handleMenuItemClick(option.text.toLowerCase());
            });
        });
    }

    handleMenuItemClick(action) {
        // Handle menu item actions
        console.log(`Menu action: ${action}`);

        // Close the menu
        this.popupMenu.classList.remove('show');

        // Example actions
        switch(action) {
            case 'home':
                window.location.href = '/';
                break;
            case 'settings':
                // Open settings
                break;
            case 'close':
                // Close panel or logout
                break;
        }
    }

    setupEventListeners() {
        // Toggle menu on button click
        this.menuToggle.addEventListener('click', (event) => {
            this.popupMenu.classList.toggle('show');
            event.stopPropagation();
        });

        // Close menu when clicking outside
        document.addEventListener('click', (event) => {
            if (!this.menuToggle.contains(event.target) && !this.popupMenu.contains(event.target)) {
                this.popupMenu.classList.remove('show');
            }
        });

        // Prevent closing when clicking inside menu
        this.popupMenu.addEventListener('click', (event) => {
            event.stopPropagation();
        });
    }
}

// Initialize popup menu
document.addEventListener('DOMContentLoaded', () => {
    new PopupMenu();
});

export default PopupMenu;