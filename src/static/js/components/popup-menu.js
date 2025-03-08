// Improved setPopupMenu function with CSS variables and bg-hover support
function setPopupMenu(options, setting, element) {
    // Check if popup already exists and is visible
    const existingPopup = document.getElementById('custom-popup-menu');
    if (existingPopup) {
        // If clicking the same element that created the popup, toggle it
        if (existingPopup.getAttribute('data-parent') === element.id) {
            document.body.removeChild(existingPopup);
            return;
        } else {
            // If clicking a different element, remove the existing popup
            document.body.removeChild(existingPopup);
        }
    }

    // Create popup container
    const popup = document.createElement('div');
    popup.id = 'custom-popup-menu';
    popup.setAttribute('data-parent', element.id);

    // First add custom classes if provided
    if (setting.classname) {
        popup.className = setting.classname;
    }

    // Add extended classes without overriding custom classname
    if (setting['classname-extend']) {
        popup.classList.add(setting['classname-extend']);
    }

    // Define and apply default popup styles
    const hasCustomClass = setting.classname || setting['classname-extend'];
    const popupStyles = {
        position: 'absolute',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        borderRadius: '8px',
        padding: '8px 0',
        zIndex: '1000',
        minWidth: '180px',
        overflow: 'hidden',
        animation: 'fadeIn 0.2s ease-out'
    };

    // Only set background if no custom classes (allowing CSS to control background)
    if (!hasCustomClass) {
        const bgColor = getComputedStyle(document.documentElement).getPropertyValue('--popup-bg').trim() || 'white';
        popupStyles.background = bgColor;
    }

    // Apply default styles as inline styles
    Object.assign(popup.style, popupStyles);

    // Add animation styles if not already added
    if (!document.getElementById('popup-menu-styles')) {
        const style = document.createElement('style');
        style.id = 'popup-menu-styles';
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        `;
        document.head.appendChild(style);
    }

    // Get element position data
    const rect = element.getBoundingClientRect();

    // Handle positioning based on location settings
    const locationKey = Object.keys(setting).find(key => key.startsWith('location-'));
    if (locationKey) {
        const [offsetX, offsetY] = setting[locationKey].split(' ').map(val => parseInt(val));

        switch (locationKey) {
            case 'location-lt': // Left-Top
                popup.style.right = (window.innerWidth - rect.left + offsetX) + 'px';
                popup.style.bottom = (window.innerHeight - rect.top + offsetY) + 'px';
                break;
            case 'location-lb': // Left-Bottom
                popup.style.right = (window.innerWidth - rect.left + offsetX) + 'px';
                popup.style.top = (rect.bottom + offsetY) + 'px';
                break;
            case 'location-rt': // Right-Top
                popup.style.left = (rect.right + offsetX) + 'px';
                popup.style.bottom = (window.innerHeight - rect.top + offsetY) + 'px';
                break;
            case 'location-rb': // Right-Bottom
                popup.style.left = (rect.right + offsetX) + 'px';
                popup.style.top = (rect.bottom + offsetY) + 'px';
                break;
            default:
                // Default to bottom-left if no valid location setting
                popup.style.left = (rect.left) + 'px';
                popup.style.top = (rect.bottom + 10) + 'px';
        }
    } else {
        // Fallback positioning if no location setting provided
        popup.style.left = (rect.left) + 'px';
        popup.style.top = (rect.bottom + 10) + 'px';
    }

            // Add menu items
    options.forEach(option => {
        // Allow for "bg-hover" option or use CSS variable
        const menuItem = document.createElement('div');

        // First apply custom classes if provided
        if (option.classname) {
            menuItem.className = option.classname;
        }

        // Add extended classes without overriding
        if (option['classname-extend']) {
            menuItem.classList.add(option['classname-extend']);
        }

        // Define default menu item styles
        const menuItemStyles = {
            display: 'flex',
            alignItems: 'center',
            padding: '10px 15px',
            cursor: 'pointer',
            transition: 'background-color 0.2s'
        };

        // Apply default styles as inline styles
        Object.assign(menuItem.style, menuItemStyles);

        // Add hover effect if no custom class is specified
        const hasCustomItemClass = option.classname || option['classname-extend'];
        if (!hasCustomItemClass) {
            // Use custom bg-hover if provided, otherwise use CSS variable or fallback
            const hoverBgColor = option['bg-hover'] ||
                                getComputedStyle(document.documentElement).getPropertyValue('--popup-hover').trim() ||
                                '#f5f5f5';

            menuItem.addEventListener('mouseover', function () {
                this.style.backgroundColor = hoverBgColor;
            });

            menuItem.addEventListener('mouseout', function () {
                this.style.backgroundColor = '';
            });
        }

        // Create icon if provided
        if (option.icon) {
            const icon = document.createElement('i');
            icon.className = option.icon;

            // Apply icon styles
            const iconStyles = {
                marginRight: '10px',
                width: '20px',
                textAlign: 'center'
            };
            Object.assign(icon.style, iconStyles);

            // Apply icon color - ensure proper color format
            if (option["icon-color"]) {
                icon.style.color = option["icon-color"];
            }

            menuItem.appendChild(icon);
        }

        // Add content
        const content = document.createElement('span');
        content.textContent = option.content;

        // Set base styles for content
        const contentStyles = {
            fontFamily: 'Arial, sans-serif',
            fontSize: '14px'
        };

        // Apply basic styles first
        Object.assign(content.style, contentStyles);

        // Apply content color if specified
        if (option["content-color"]) {
            content.style.color = option["content-color"];
        }

        menuItem.appendChild(content);

        // Add click event
        menuItem.addEventListener('click', function (e) {
            e.stopPropagation();
            if (typeof option.action === 'function') {
                option.action();
            }
            document.body.removeChild(popup);
        });

        popup.appendChild(menuItem);
    });

    // Add close on outside click
    const closePopup = function (e) {
        if (!popup.contains(e.target) && e.target !== element) {
            document.body.removeChild(popup);
            document.removeEventListener('click', closePopup);
        }
    };

    // Delay adding the event listener to prevent immediate closing
    setTimeout(() => {
        document.addEventListener('click', closePopup);
    }, 100);

    // Add to document
    document.body.appendChild(popup);
}