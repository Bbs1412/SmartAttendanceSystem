// ======================================================================================
// Theme switch functionality:
// ======================================================================================

const themeSwitch = document.getElementById('switch-button');

themeSwitch.addEventListener('change', () => {
    if (themeSwitch.checked) {
        document.documentElement.setAttribute('data-theme', 'light');
        // document.getElementById('placeholderImage').src = '/assets/camera_light.jpg';
        console.info('JS: Light theme activated');
    } else {
        document.documentElement.removeAttribute('data-theme');
        // document.getElementById('placeholderImage').src = '/assets/camera2.jpg';
        console.info('JS: Dark theme activated');
    }
});
