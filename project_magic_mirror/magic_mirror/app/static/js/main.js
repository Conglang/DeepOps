'use strict';


var video = window.video = document.querySelector('video');
var canvas = window.canvas = document.querySelector('canvas');
canvas.width = 480;
canvas.height = 360;

var constraints = {
    audio: true,
    video: true
};

var sampleRate = 44100;
var recording = true;
var photos = [];
var photoNum = 5;
var snapshotTimer;
var audioStream;
var videoStream;

var ws = new WebSocket('ws://127.0.0.1:5000/websocket');


ws.onopen = function(evt) {
    console.log('Connected to websocket.');
    // First message: send the sample rate
    ws.send("sample rate:" + sampleRate);
    ws.send("photo num:" + photoNum);
    ws.send("photo width:" + canvas.width);
    ws.send("photo height:" + canvas.height);
    navigator.mediaDevices.getUserMedia(constraints).then(handleSuccess).catch(handleError);
}

function flatten_image(imgData) {
    console.log(canvas.width * canvas.height * 3);
    var buf = new Int16Array(canvas.width * canvas.height * 3);
    var cur = 0;
    for (var i = 0; i < imgData.data.length; i += 4)
    {
        buf[cur++] = imgData.data[i+0];
        buf[cur++] = imgData.data[i+1];
        buf[cur++] = imgData.data[i+2];
    }
    return buf;
}

function takeSnapshot() {
    var imgData;
    var ctx = canvas.getContext('2d')
    ctx.drawImage(video, canvas.width / 2 - canvas.width / 2, 0, canvas.width, canvas.height);
    var imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    
    var img = flatten_image(imgData)
    console.log(img);
    return img;
}

function convertFloat32ToInt16(buffer) {
    var l = buffer.length;
    var buf = new Int16Array(l);
    while (l--) {
      buf[l] = Math.min(1, buffer[l])*0x7FFF;
    }
    return buf.buffer;
}

function recorderProcess(e) {
    if (recording) {
        var left = e.inputBuffer.getChannelData(0);
        ws.send(convertFloat32ToInt16(left));
    }
}

function takeEnoughPhotosAndGoOn() {
    if (photos.length < photoNum) {
        // take photos and send
        console.log('take image ', photos.length, photoNum);
        var img = takeSnapshot()
        photos.push(img)
        ws.send(img)
    } else {
        console.log('connect audio');
        clearInterval(snapshotTimer);
        // audio stream
        construcAudioStream()
    }
}

function construcAudioStream() {
    // audio preprocess
    var audio_context = new AudioContext;
    sampleRate = audio_context.sampleRate;
    var audioInput = audio_context.createMediaStreamSource(audioStream);
    var bufferSize = 4096;
    // record only 1 channel
    var recorder = audio_context.createScriptProcessor(bufferSize, 1, 1);
    // specify the processing function
    recorder.onaudioprocess = recorderProcess;
    // connect stream to our recorder
    audioInput.connect(recorder);
    // connect out recorder to the previous destination
    recorder.connect(audio_context.destination);
}

function handleSuccess(stream) {
    console.log('handleSuccess');
    // get audio and video stream
    audioStream = new MediaStream(stream.getAudioTracks());
    videoStream = new MediaStream(stream.getVideoTracks());

    // draw video on the screen
    window.stream = stream; // make stream available to browser console
    video.srcObject = videoStream;

    // first take 5 pictures of the user and then send audio stream
    snapshotTimer = window.setInterval(takeEnoughPhotosAndGoOn, 1000);
}

function handleError(error) {
  console.log('navigator.getUserMedia error: ', error);
}