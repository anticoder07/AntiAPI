class NotificationManager {
    constructor(options = {}) {
        // Cấu hình mặc định
        this.config = {
            maxNotifications: options.maxNotifications || 5, // Số lượng thông báo tối đa
            duration: options.duration || 5000, // Thời gian hiển thị mặc định (5 giây)
            position: options.position || 'top-right', // Vị trí hiển thị
            containerClass: 'notification-container'
        };

        // Khởi tạo container chứa thông báo
        this.initContainer();

        // Track active notifications count
        this.activeNotifications = 0;
    }

    // Tạo container chứa thông báo
    initContainer() {
        // Kiểm tra nếu container đã tồn tại
        if (document.querySelector(`.${this.config.containerClass}`)) return;

        const container = document.createElement('div');
        container.className = `${this.config.containerClass} ${this.config.position}`;
        document.body.appendChild(container);

        // Thêm CSS inline để tránh phụ thuộc vào file CSS ngoài
        container.style.cssText = `
            position: fixed;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 10px;
            padding: 15px;
            max-width: 350px;
            width: 100%;
            box-sizing: border-box;
            ${this.getPositionStyles()}
            pointer-events: none; /* Allow clicks to pass through when empty */
        `;
    }

    // Lấy style vị trí của container
    getPositionStyles() {
        switch(this.config.position) {
            case 'top-right':
                return 'top: 15px; right: 15px;';
            case 'top-left':
                return 'top: 15px; left: 15px;';
            case 'bottom-right':
                return 'bottom: 15px; right: 15px;';
            case 'bottom-left':
                return 'bottom: 15px; left: 15px;';
            default:
                return 'top: 15px; right: 15px;';
        }
    }

    // Xác định màu sắc và icon cho từng loại thông báo
    getNotificationStyles(type) {
        const styles = {
            success: {
                backgroundColor: 'var(--api-get, #10b981)',
                textColor: 'var(--text-color, white)',
                icon: '✓'
            },
            error: {
                backgroundColor: 'var(--error-color, #f03e3e)',
                textColor: 'var(--text-color, white)',
                icon: '✘'
            },
            warning: {
                backgroundColor: 'var(--api-patch, #f59e0b)',
                textColor: 'var(--text-color, white)',
                icon: '⚠️'
            },
            info: {
                backgroundColor: 'var(--api-post, #3b82f6)',
                textColor: 'var(--text-color, white)',
                icon: 'ℹ️'
            }
        };
        return styles[type] || styles.info;
    }

    // Update container visibility based on notifications count
    updateContainerVisibility() {
        const container = document.querySelector(`.${this.config.containerClass}`);

        if (this.activeNotifications === 0) {
            // Make container completely invisible when no notifications
            container.style.display = 'none';
        } else {
            container.style.display = 'flex';
            container.style.pointerEvents = 'auto'; // Enable interaction when there are notifications
        }
    }

    // Hiển thị thông báo
    show(message, type = 'info', duration = null) {
        // Lấy container
        const container = document.querySelector(`.${this.config.containerClass}`);

        // Ensure container is visible
        container.style.display = 'flex';
        container.style.pointerEvents = 'auto';

        // Track this notification
        this.activeNotifications++;
        this.updateContainerVisibility();

        // Kiểm tra số lượng thông báo
        if (container.children.length >= this.config.maxNotifications) {
            // Xóa thông báo cũ nhất nếu vượt quá giới hạn
            container.removeChild(container.firstChild);
            this.activeNotifications--; // Decrease count because we removed one
        }

        // Tạo phần tử thông báo
        const notification = document.createElement('div');
        const notificationStyle = this.getNotificationStyles(type);

        notification.style.cssText = `
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 15px 18px;
            border-radius: 8px;
            color: ${notificationStyle.textColor};
            background-color: ${notificationStyle.backgroundColor};
            box-shadow: 0 4px 6px var(--popup-shadow, rgba(0,0,0,0.1));
            animation: slideIn 0.3s ease-out;
            cursor: pointer;
            font-size: 15px;
            pointer-events: auto;
        `;

        // Nội dung thông báo
        notification.innerHTML = `
            <span>${notificationStyle.icon}</span>
            <span>${message}</span>
        `;

        // Thêm sự kiện click để đóng thông báo sớm
        notification.addEventListener('click', () => this.remove(notification));

        // Thêm thông báo vào container
        container.appendChild(notification);

        // Tự động xóa thông báo sau một khoảng thời gian
        const notificationDuration = duration || this.config.duration;
        const timer = setTimeout(() => {
            this.remove(notification);
        }, notificationDuration);

        // Hủy timer nếu di chuột vào thông báo
        notification.addEventListener('mouseenter', () => clearTimeout(timer));
    }

    // Xóa thông báo
    remove(notification) {
        notification.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => {
            notification.remove();
            this.activeNotifications--;
            this.updateContainerVisibility();
        }, 300);
    }

    // Thêm CSS animation
    static injectAnimations() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

NotificationManager.injectAnimations();

const Notification = new NotificationManager({
    maxNotifications: 3,
    duration: 2500,
    position: 'top-right'
});

window.Notification = Notification;