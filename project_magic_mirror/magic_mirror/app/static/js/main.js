'use strict';


var video = window.video = document.querySelector('video');
var canvas = window.canvas = document.querySelector('canvas');
canvas.width = 480;
canvas.height = 360;

var constraints = {
    audio: true,
    video: true
};

var sampleRate = 44100
var recording = true

var ws = new WebSocket('ws://127.0.0.1:5000/websocket');


ws.onopen = function(evt) {
    console.log('Connected to websocket.');
    // First message: send the sample rate
    ws.send("sample rate:" + sampleRate);
    navigator.mediaDevices.getUserMedia(constraints).then(handleSuccess).catch(handleError);
}

function takeSnapshot() {
    //canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
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

function handleSuccess(stream) {
    // get audio and video stream
    var audioStream = new MediaStream(stream.getAudioTracks());
    var videoStream = new MediaStream(stream.getVideoTracks());
    
    // draw video on the screen
    window.stream = stream; // make stream available to browser console
    video.srcObject = videoStream;
    
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

function handleError(error) {
  console.log('navigator.getUserMedia error: ', error);
}


