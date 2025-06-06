document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-bs-toggle="password"]').forEach(function (element) {
        element.addEventListener('click', function (e) {
            e.preventDefault(); // prevent form submission if inside a form
            let targetSelector = element.getAttribute('data-target');
            let iconSelector = element.getAttribute('data-icon');

            let target = document.querySelector(targetSelector);
            let icon = document.querySelector(iconSelector);

            if (target) {
                if (target.type === 'password') {
                    target.type = 'text';
                    if (icon) {
                        icon.classList.remove('eye-closed');
                        icon.classList.add('eye-open');
                    }
                } else {
                    target.type = 'password';
                    if (icon) {
                        icon.classList.remove('eye-open');
                        icon.classList.add('eye-closed');
                    }
                }
            }
        });
    });
});
