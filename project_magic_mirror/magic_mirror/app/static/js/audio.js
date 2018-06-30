var last_audio = ""

window.onload = function () {
    window.setInterval(requestAudioFile, 500);
}

function requestAudioFile() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/getFileName', true);
    xhr.send();
    xhr.onreadystatechange = function() {
        if (this.readyState == 4) {
            var filePath = this.responseText;
            if (filePath != "" && filePath != last_audio) {
                localStorage.setItem("constraints.audio", false);
                var audio = document.getElementById('currentAudio')
                audio.src = filePath;
                audio.load();
                audio.oncanplaythrough = function() {
                    console.log('can play ', filePath);
                    this.play();
                }
            } else {
                localStorage.setItem("constraints.audio", true);
            }
            last_audio = filePath
        }
    }
}