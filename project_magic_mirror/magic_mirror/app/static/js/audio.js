var xhr = new XMLHttpRequest();
xhr.open('GET', '/getFileName', true);
xhr.send();

xhr.onreadystatechange = function() {
    window.setInterval(playAudio, 500);
}

function playAudio() {
    // console.log('audio file: ', this.responseText);
    if (this.readyState == 4) {
        var filePath = this.responseText;
        var audio = document.getElementById('currentAudio')
        audio.src = filePath;
        audio.load();
        audio.oncanplaythrough = function() {
            console.log('can play ', filePath);
            this.play();
        }
    }
}