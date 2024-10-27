document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-bs-toggle="password"]').forEach(function (element) {
        element.addEventListener('click', function (e) {
            e.preventDefault(); // Prevent form submission if inside a form
            let targetSelector = element.getAttribute('data-target');
            let iconSelector = element.getAttribute('data-icon');

            let target = document.querySelector(targetSelector);
            let icon = document.querySelector(iconSelector);

            if (target) {
                if (target.type === 'password') {
                    target.type = 'text';
                    if (icon) {
                        icon.classList.remove('bi-eye-slash');
                        icon.classList.add('bi-eye');
                    }
                } else {
                    target.type = 'password';
                    if (icon) {
                        icon.classList.remove('bi-eye');
                        icon.classList.add('bi-eye-slash');
                    }
                }
            }
        });
    });
});
