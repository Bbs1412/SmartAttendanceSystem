let mediaRecorder;
let recordedBlobs;
let stream;

let startTimestamp;
let endTimestamp;

let temp;
// let no_of_frames_to_send = 100;
let no_of_frames_to_send = 20;


const video = document.querySelector('video');
const cameraButton = document.getElementById('startCamera');
const startButton = document.getElementById('startRecord');
const stopButton = document.getElementById('stopRecord');
const submitButton = document.querySelector('input[type="submit"]');

const mn = document.getElementById('main');
const err_box = document.getElementById('errBox');

startButton.disabled = true;
cameraButton.addEventListener('click', () => {
    init({ video: true });
    startButton.disabled = false;
    // Hide the placeholder and show the video
    document.getElementById('placeholderImage').style.display = 'none';
    document.getElementById('video').style.display = 'block';
});

startButton.addEventListener('click', () => {
    // startTimestamp = new Date().toISOString(); // Capture start timestamp
    startTimestamp = new Date();
    startRecording();
    startButton.disabled = true;
    stopButton.disabled = false;
    submitButton.disabled = true;
});

stopButton.addEventListener('click', () => {
    endTimestamp = new Date();
    stopRecording();
    startButton.disabled = true;
    stopButton.disabled = true;
    // submitButton.disabled = false; // let this be handled by frame extractor function
    document.getElementById("extracting_wait").style.display = 'flex';
    releaseCamera();
});

submitButton.addEventListener('click', (e) => {
    e.preventDefault();
    submitForm();
});

async function init(constraints) {
    try {
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        handleSuccess(stream);
    } catch (e) {
        console.error('navigator.getUserMedia error:', e);
    }
}

function handleSuccess(stream) {
    video.srcObject = stream;
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
        console.error('Exception while creating MediaRecorder:', e);
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

function handleDataAvailable(event) {
    if (event.data && event.data.size > 0) {
        recordedBlobs.push(event.data);
    }
}

function releaseCamera() {
    console.log('JS: Released Camera')
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    video.srcObject = null;
}



async function extractFrames(videoBlob, no_of_frames_to_send) {
    const debug = true;

    console.log('JS: Extract frames activated');
    const videoElement = document.createElement('video');
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    videoElement.src = URL.createObjectURL(videoBlob);

    if (debug) { console.log('JS: [1/n] Video context received'); }
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
    if (debug) { console.log('JS: [2/n] Video interval to extract', interval); }

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

                if (debug) { console.log(`JS: [Frame ${i + 1}] Captured at time ${desiredTime}`); }

                resolve();
            };
        });
    }

    if (debug) { console.log('JS: [3a/n] Intermediate: Frames: ', frames.length); }
    if (debug) { console.log('JS: [3b/n] Intermediate: Timestamps: ', timestamps.length); }

    if (frames.length < no_of_frames_to_send) {
        for (let i = frames.length; i < no_of_frames_to_send; i++) {
            frames.push(frames[frames.length - 1]);
            timestamps.push(timestamps[timestamps.length - 1]);
        }
    }

    if (debug) { console.log('JS: [4a/n] Final: Frames: ', frames.length); }
    if (debug) { console.log('JS: [4b/n] Final: Timestamps: ', timestamps.length); }

    document.getElementById('videoData').value = JSON.stringify(frames);
    document.getElementById('timestamps').value = JSON.stringify(timestamps);

    if (debug) { console.log('JS: [n/n] Form data updated'); }

    // Enable submit button
    document.getElementById('extracting_wait').style.display = 'none';
    submitButton.disabled = false;
}

// ------------------------------------------------------


// submit these: num_students, student_names, video_data, timestamps
// vid data is no_of_frames_to_send images in base64
function submitForm() {
    console.log('JS: Submit form activated')
    const form = document.getElementById('uploadForm');
    const formData = new FormData(form);

    // debug
    temp = formData;

    mn.style.cssText = 'filter: blur(2px)';
    err_box.style.display = 'flex';
    document.getElementById('proc_stat').style.display = 'flex';


    fetch('/upload_video', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
        .then(data => {
            console.log(data);

            if (data.status === 'success') {
                // console.log("Vid Sent Successfully");
                document.getElementById('upload_status').innerHTML = "<p>✅ Video Sent Successfully!<p>";
                document.getElementById('attendance_div').style.display = 'flex';
                document.getElementById('proc_stat').style.display = 'flex';

                calculate_attendance();
            }

        });
}

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
