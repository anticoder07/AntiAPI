/**
 * Theme Toggle Component
 * Handles switching between light and dark themes
 */
class ThemeToggle {
    constructor() {
        this.themeToggleBtn = document.getElementById('theme-toggle');
        this.themeIcon = this.themeToggleBtn?.querySelector('i');

        if (!this.themeToggleBtn) return;

        this.init();
        this.setupEventListeners();
    }

    init() {
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            document.documentElement.setAttribute('data-theme', 'dark');
            this.themeIcon.classList.replace('fa-moon', 'fa-sun');
        }
    }

    setupEventListeners() {
        this.themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';

            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);

            if (newTheme === 'dark') {
                this.themeIcon.classList.replace('fa-moon', 'fa-sun');
            } else {
                this.themeIcon.classList.replace('fa-sun', 'fa-moon');
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ThemeToggle();
});

export default ThemeToggle;