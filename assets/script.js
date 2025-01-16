// script.js


// ======================================================================================
// Global variables:
// ======================================================================================

let no_of_frames_to_send = 20;

let mediaRecorder;
let recordedBlobs;
let stream;

let temp;
let startTimestamp;
let endTimestamp;

const video_box = document.querySelector('video');
const video_placeholder = document.getElementById('placeholder');
const err_box = document.getElementById('errBox');

const cameraButton = document.getElementById('startCamera');
const startRecordingBtn = document.getElementById('startRecord');
const stopRecordingBtn = document.getElementById('stopRecord');
const submitButton = document.querySelector('button[type="submit"]');


cameraButton.disabled = false;
startRecordingBtn.disabled = true;
stopRecordingBtn.disabled = true;
submitButton.disabled = true;

const show_logs = true;
if (show_logs) { console.log('JS: Script loaded successfully'); }


// ======================================================================================
// Camera Ops:
// ======================================================================================

// Initialize camera:
async function initialize_camera(constraints) {
    try {
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        show_live_video(stream);
        console.log('JS: Camera initialized successfully');
    } catch (e) {
        console.log('JS: Failed to initialize camera');
        console.error('navigator.getUserMedia error:', e);
    }
}


// Fn which runs if camera is initialized successfully
function show_live_video(stream) {
    console.log('JS: Showing live video')
    video_box.srcObject = stream;
}


function startRecording() {
    console.log('JS: Recording started')
    recordedBlobs = [];
    let options = { mimeType: 'video/webm;codecs=vp9' };
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options = { mimeType: 'video/webm;codecs=vp8' };
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            options = { mimeType: 'video/webm' };
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options = { mimeType: '' };
            }
        }
    }

    try {
        mediaRecorder = new MediaRecorder(stream, options);
    } catch (e) {
        console.error('JS: Exception while creating MediaRecorder:', e);
        return;
    }

    mediaRecorder.onstop = (event) => {
        const superBuffer = new Blob(recordedBlobs, { type: 'video/webm' });
        extractFrames(superBuffer, no_of_frames_to_send);
    };

    mediaRecorder.ondataavailable = handleDataAvailable;
    mediaRecorder.start(10);
}


function stopRecording() {
    console.log('JS: Recording stopped')
    mediaRecorder.stop();
}


function releaseCamera() {
    console.log('JS: Released Camera')
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    video_box.srcObject = null;
}


// ======================================================================================
// Event Listeners to the buttons and call the respective functions:
// ======================================================================================

cameraButton.addEventListener('click', () => {
    initialize_camera({ video: true });
    startRecordingBtn.disabled = false;
    // Hide the placeholder and show the video
    video_placeholder.style.display = 'none';
    video_box.style.display = 'block';
});


startRecordingBtn.addEventListener('click', () => {
    // // Capture start timestamp
    // startTimestamp = new Date().toISOString();
    startTimestamp = new Date();
    startRecording();
    startRecordingBtn.disabled = true;
    stopRecordingBtn.disabled = false;
    submitButton.disabled = true;
});

stopRecordingBtn.addEventListener('click', () => {
    endTimestamp = new Date();
    stopRecording();
    startRecordingBtn.disabled = true;
    stopRecordingBtn.disabled = true;
    // submitButton.disabled = false; // let this be handled by frame extractor function
    document.getElementById("extracting_wait").style.display = 'flex';
    releaseCamera();
});

submitButton.addEventListener('click', (e) => {
    e.preventDefault();
    submitForm();
});


// ======================================================================================
// Post processing: Frame Extraction and all...:
// ======================================================================================

// Fn to pass the recorded data to the recordedBlobs array
function handleDataAvailable(event) {
    if (event.data && event.data.size > 0) {
        recordedBlobs.push(event.data);
    }
}

// Fn to extract defined # of frames from the video at regular intervals:
async function extractFrames(videoBlob, no_of_frames_to_send) {
    console.log('JS: Extract frames activated');
    const videoElement = document.createElement('video');
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    videoElement.src = URL.createObjectURL(videoBlob);

    if (show_logs) { console.log('JS: [1/n] Video context received'); }
    await new Promise(resolve => {
        videoElement.onloadedmetadata = () => {
            canvas.width = videoElement.videoWidth;
            canvas.height = videoElement.videoHeight;
            resolve();
        };
    });

    const totalDuration = (endTimestamp - startTimestamp) / 1000; // Total duration in seconds
    const interval = totalDuration / no_of_frames_to_send; // Gap between frames in seconds
    let frames = [];
    let timestamps = [];
    if (show_logs) { console.log('JS: [2/n] Video interval to extract', interval); }

    for (let i = 0; i < no_of_frames_to_send; i++) {
        const desiredTime = i * interval;
        videoElement.currentTime = desiredTime;

        await new Promise(resolve => {
            videoElement.onseeked = () => {
                context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
                frames.push(canvas.toDataURL('image/jpeg'));

                // Calculate the timestamp for this frame
                let frameTimestamp = new Date(startTimestamp.getTime() + desiredTime * 1000);
                timestamps.push(frameTimestamp.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }));

                if (show_logs) { console.log(`JS: [Frame ${i + 1}] Captured at time ${desiredTime}`); }

                resolve();
            };
        });
    }

    if (show_logs) { console.log('JS: [3a/n] Intermediate: Frames: ', frames.length); }
    if (show_logs) { console.log('JS: [3b/n] Intermediate: Timestamps: ', timestamps.length); }

    if (frames.length < no_of_frames_to_send) {
        for (let i = frames.length; i < no_of_frames_to_send; i++) {
            frames.push(frames[frames.length - 1]);
            timestamps.push(timestamps[timestamps.length - 1]);
        }
    }

    if (show_logs) { console.log('JS: [4a/n] Final: Frames: ', frames.length); }
    if (show_logs) { console.log('JS: [4b/n] Final: Timestamps: ', timestamps.length); }

    document.getElementById('videoData').value = JSON.stringify(frames);
    document.getElementById('timestamps').value = JSON.stringify(timestamps);

    if (show_logs) { console.log('JS: [n/n] Form data updated'); }

    // Enable submit button
    document.getElementById('extracting_wait').style.display = 'none';
    submitButton.disabled = false;
}


// ======================================================================================
// Form submission:
// ======================================================================================

// submit these: num_students, student_names, video_data, timestamps
// vid data is no_of_frames_to_send images in base64
function submitForm() {
    console.log('JS: Submit form activated')
    const form = document.getElementById('uploadForm');
    const formData = new FormData(form);

    // show_logs
    temp = formData;

    err_box.style.display = 'flex';
    document.getElementById('proc_stat').style.display = 'block';


    fetch('/upload_video', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
        .then(data => {
            console.log(data);

            if (data.status === 'success') {
                console.log("JS: Vid Sent Successfully");
                document.getElementById('upload_status').innerHTML = "<p>✅ Video Sent Successfully!<p>";

                calculate_attendance();
            }
        });
}


// ======================================================================================
// Result part:
// ======================================================================================

function calculate_attendance() {
    console.log('JS: Started attendance calculation on server!')

    fetch('/calc_attendance', {
        method: 'GET',
    }).then(response => response.json())
        .then(data => {
            console.log("Attendance status: ", data);

            if (data.status === 'completed') {
                console.log('JS: Attendance calculation Completed!')
                console.log('JS: Getting results from server!')
                window.location.href = '/results';
            }

            else {
                window.alert("Sorry, some error occurred on server side!")
            }
        })
}


// ======================================================================================
// Theme switch functionality:
// ======================================================================================
const themeSwitch = document.getElementById('switch-button');

themeSwitch.addEventListener('change', () => {
    if (themeSwitch.checked) {
        document.documentElement.setAttribute('data-theme', 'light');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
});