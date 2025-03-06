function createPopup(onSubmit, fields, title_input) {
    // Thêm font Roboto
    const fontLink = document.createElement('link');
    fontLink.rel = 'stylesheet';
    fontLink.href = 'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap';
    document.head.appendChild(fontLink);

    // Tạo overlay
    const overlay = document.createElement('div');
    overlay.classList.add('popup-overlay');
    overlay.addEventListener('click', closePopup);

    // Style cho overlay
    Object.assign(overlay.style, {
        display: 'none',
        position: 'fixed',
        top: '0',
        left: '0',
        width: '100%',
        height: '100%',
        background: 'rgba(0, 0, 0, 0.6)',
        backdropFilter: 'blur(5px)',
        zIndex: '9998',
        opacity: '0',
        transition: 'opacity 0.3s ease'
    });

    // Tạo container popup
    const popup = document.createElement('div');
    popup.classList.add('popup-container');

    // Style cho container với màu từ theme
    Object.assign(popup.style, {
        display: 'none',
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%) scale(0.9)',
        background: 'var(--popup-bg, white)',
        padding: '25px',
        boxShadow: '0 10px 30px var(--popup-shadow, rgba(0, 0, 0, 0.2))',
        borderRadius: '12px',
        textAlign: 'left',
        minWidth: '350px',
        maxWidth: '90%',
        zIndex: '9999',
        fontFamily: "'Roboto', sans-serif",
        opacity: '0',
        transition: 'opacity 0.3s ease, transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
        border: '1px solid var(--popup-border, #e0e0e0)'
    });

    // Tạo tiêu đề
    const title = document.createElement('h3');
    title.innerText = title_input;
    Object.assign(title.style, {
        margin: '0 0 20px 0',
        color: 'var(--text-color, #333)',
        fontSize: '22px',
        fontWeight: '600',
        textAlign: 'center',
        paddingBottom: '12px',
        borderBottom: '1px solid var(--border-color, #eee)'
    });
    popup.appendChild(title);

    // Kiểm tra nếu đang ở dark mode
    const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';

    // Tạo các trường nhập liệu
    fields.forEach(field => {
        const wrapper = document.createElement('div');
        Object.assign(wrapper.style, {
            marginBottom: '16px',
            display: 'flex',
            flexDirection: 'column'
        });

        const label = document.createElement('label');
        label.innerText = field.label;
        label.setAttribute('for', field.key);

        // Sửa màu label để hiển thị tốt hơn trong dark mode
        Object.assign(label.style, {
            fontWeight: '500',
            marginBottom: '6px',
            color: isDarkMode ? 'white' : 'var(--text-label, #444)',
            fontSize: '14px'
        });

        const input = document.createElement('input');
        input.id = field.key;
        input.type = 'text';
        input.placeholder = field.placeholder;
        Object.assign(input.style, {
            padding: '12px',
            borderRadius: '8px',
            border: '1px solid var(--input-border, #ddd)',
            outline: 'none',
            transition: 'all 0.3s',
            fontSize: '15px',
            color: 'var(--text-color, #000)',
            backgroundColor: 'var(--input-bg, white)'
        });

        // Thêm event listeners cho input
        input.addEventListener('focus', function () {
            this.style.borderColor = 'var(--primary-color, #4CAF50)';
            this.style.boxShadow = '0 0 0 2px var(--primary-shadow, rgba(76, 175, 80, 0.2))';
        });

        input.addEventListener('blur', function () {
            this.style.borderColor = 'var(--input-border, #ddd)';
            this.style.boxShadow = 'none';
        });

        wrapper.appendChild(label);
        wrapper.appendChild(input);
        popup.appendChild(wrapper);
    });

    // Tạo container cho các nút - đổi thứ tự hiển thị
    const btnContainer = document.createElement('div');
    Object.assign(btnContainer.style, {
        display: 'flex',
        justifyContent: 'center',
        gap: '12px',
        marginTop: '24px'
    });

    // Tạo nút Cancel
    const cancelBtn = document.createElement('button');
    cancelBtn.innerText = 'Cancel';
    Object.assign(cancelBtn.style, {
        padding: '12px 20px',
        border: 'none',
        borderRadius: '8px',
        color: 'white',
        cursor: 'pointer',
        fontSize: '15px',
        fontWeight: '500',
        transition: 'all 0.2s',
        minWidth: '100px',
        background: 'var(--api-delete, #f44336)'
    });
    cancelBtn.addEventListener('click', closePopup);

    // Thêm hover effect cho nút Cancel
    cancelBtn.addEventListener('mouseover', function () {
        this.style.background = '#e53935';
        this.style.transform = 'translateY(-2px)';
        this.style.boxShadow = '0 4px 8px rgba(244, 67, 54, 0.3)';
    });

    cancelBtn.addEventListener('mouseout', function () {
        this.style.background = 'var(--api-delete, #f44336)';
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = 'none';
    });

    // Tạo nút Submit (Save) - bây giờ sẽ là nút thứ hai (bên phải)
    const submitBtn = document.createElement('button');
    submitBtn.innerText = 'Save';
    Object.assign(submitBtn.style, {
        padding: '12px 20px',
        border: 'none',
        borderRadius: '8px',
        color: 'white',
        cursor: 'pointer',
        fontSize: '15px',
        fontWeight: '500',
        transition: 'all 0.2s',
        minWidth: '100px',
        background: 'var(--primary-color, #4CAF50)'
    });
    submitBtn.addEventListener('click', submitForm);

    // Thêm hover effect cho nút Submit
    submitBtn.addEventListener('mouseover', function () {
        this.style.background = 'var(--primary-color, #3e9142)';
        this.style.transform = 'translateY(-2px)';
        this.style.boxShadow = '0 4px 8px var(--primary-shadow-hover, rgba(76, 175, 80, 0.3))';
    });

    submitBtn.addEventListener('mouseout', function () {
        this.style.background = 'var(--primary-color, #4CAF50)';
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = 'none';
    });

    // Thêm nút theo thứ tự: Cancel ở trái, Save ở phải
    btnContainer.appendChild(cancelBtn);
    btnContainer.appendChild(submitBtn);
    popup.appendChild(btnContainer);

    document.body.appendChild(overlay);
    document.body.appendChild(popup);

    // Thêm một MutationObserver để theo dõi các thay đổi theme
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'data-theme') {
                const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';
                // Cập nhật màu label
                const labels = popup.querySelectorAll('label');
                labels.forEach(label => {
                    label.style.color = isDarkMode ? 'white' : 'var(--text-label, #444)';
                });
            }
        });
    });

    // Bắt đầu theo dõi thay đổi trong thuộc tính data-theme
    observer.observe(document.documentElement, { attributes: true });

    function openPopup() {
        const popup = document.querySelector('.popup-container');
        const overlay = document.querySelector('.popup-overlay');

        // Kiểm tra lại dark mode khi mở popup
        const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';
        const labels = popup.querySelectorAll('label');
        labels.forEach(label => {
            label.style.color = isDarkMode ? 'white' : 'var(--text-label, #444)';
        });

        popup.style.display = 'block';
        overlay.style.display = 'block';

        // Trigger reflow để animation hoạt động
        void popup.offsetWidth;

        popup.style.opacity = '1';
        popup.style.transform = 'translate(-50%, -50%) scale(1)';
        overlay.style.opacity = '1';
    }

    function closePopup() {
        const popup = document.querySelector('.popup-container');
        const overlay = document.querySelector('.popup-overlay');

        popup.style.opacity = '0';
        popup.style.transform = 'translate(-50%, -50%) scale(0.9)';
        overlay.style.opacity = '0';

        // Đợi animation hoàn thành rồi ẩn popup
        setTimeout(() => {
            popup.style.display = 'none';
            overlay.style.display = 'none';
        }, 300);
    }

    function submitForm() {
        let formData = {};
        fields.forEach(field => {
            formData[field.key] = document.getElementById(field.key).value;
        });

        // Gọi hàm onSubmit được truyền vào thay vì console.log
        if (typeof onSubmit === 'function') {
            onSubmit(formData);
        }

        closePopup();
    }

    // Trả về các hàm để có thể gọi từ bên ngoài
    return {
        open: openPopup,
        close: closePopup
    };
}