// ======================================================================================
// Theme switch functionality:
// ======================================================================================

const themeSwitch = document.getElementById('switch-button');

themeSwitch.addEventListener('change', () => {
    if (themeSwitch.checked) {
        document.documentElement.setAttribute('data-theme', 'light');
        // document.getElementById('placeholderImage2').src = '/assets/camera_light.jpg';
    } else {
        document.documentElement.removeAttribute('data-theme');
        // document.getElementById('placeholderImage2').src = '/assets/camera2.jpg';
    }
});
