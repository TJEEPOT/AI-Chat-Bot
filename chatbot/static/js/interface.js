const botName = "TransportBot";
const recordTimeout = 20000;
var useTextToSpeech = new Boolean(true);    // needs to be set somewhere in ui by function
var chosenVoice = null; // set on load to avoid problems with async func


document.getElementById("message-input-box").addEventListener('keyup', function (e){
    if (e.code === 'Enter'){
        e.preventDefault();
        document.getElementById("message-submit").click();
    }
})
var rec_button = document.getElementById('record-button');
var rec_span = document.getElementById('record-button-span');

window.speechSynthesis.onvoiceschanged=()=>{
    let voiceList = speechSynthesis.getVoices();
    chosenVoice = voiceList[4];     // not sure how to avoid this
}

window.addEventListener('DOMContentLoaded', ()=>{

    navigator.mediaDevices.getUserMedia({audio: true}).then(async function(stream) {
    let rtcRecorder = RecordRTC(stream, {
        type: 'audio', mimeType: 'audio/wav', recorderType: RecordRTC.StereoAudioRecorder
    });
    rec_button.addEventListener("click", ()=>{
        if (rtcRecorder.getState() === "inactive"){
            rtcRecorder.startRecording();
            setTimeout(()=>{
                stopRec();
            },recordTimeout)
            rec_span.innerHTML = 'stop';
            rec_span.style.color = 'red';
        } else {
            stopRec();
        }
        function stopRec(){
                if (rtcRecorder.getState() === "recording"){
                    rtcRecorder.stopRecording(function (){
                    let audioBlob = rtcRecorder.getBlob();
                    sendAudio(audioBlob);
                    rtcRecorder.reset();
                });
                rec_span.innerHTML = 'record_voice_over';
                rec_span.style.color = 'white';
                }
        }
    });
});
})

function toggleTextToSpeech(){
    useTextToSpeech = !useTextToSpeech;
}

function submit(){
            inputBox = document.getElementById("message-input-box");
            userMessage = inputBox.value
            if (userMessage !== ""){
                // display message
            addMessage(inputBox.value, "human-message", "You")
            response = fetch('get_reply', {
              method: 'post',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify(userMessage)
            }).then(function (response){
                response.json().then(function (data){
                    console.log(response);
                    console.log(data);
                    // take response here
                    addMessage(data.message, "bot-message", botName);
                    if (useTextToSpeech){readMessage(data.message);};
                })
            });
            inputBox.value = "";
            }
}

function readMessage(message){
        if ('speechSynthesis' in window){
            let speechMessage = new SpeechSynthesisUtterance(message);
            speechMessage.voice = chosenVoice;
            speechSynthesis.speak(speechMessage);

        }else{
            console.log("Browser does not support speech synthesis!")
        }



}

function addMessage(message, userType, name){
    var date = new Date()
    const baseHTML = ` <div class="${userType}">
                <div class="main-message-wrapper">
                    <div class="user-message-header">
                        <div class="user-message-name">${name}</div>
                        <div class="user-message-time">${("0" + date.getHours()).slice(-2)}:${("0" + date.getMinutes()).slice(-2)}</div>
                    </div>
                    <div class="user-message-content">
                        ${message}
                    </div>
                </div>
            </div>
            `;
    document.getElementById("chat-box").insertAdjacentHTML('beforeend', baseHTML);
    document.getElementById("chat-box").scrollTop = document.getElementById("chat-box").scrollHeight
    document.getElementById("message-input-box").scrollIntoView({block:"start", behavior: "smooth"})
}

function sendAudio(audio){
    const formData = new FormData();
    formData.append('file', audio);
    console.log(audio);
    response = fetch('get_audio', {
              method: 'post',
              body: formData
            }).then(function (response){
                response.json().then(function (data){
                    console.log(data);
                    // take response here
                    document.getElementById('message-input-box').value = data['message'];
                })
            });
}


addMessage("Hello! Let me know what I can help you with.", "bot-message",botName);
addMessage("For testing, try giving me a message in the following format: CRS1, CRS2, date, time. e.g.: NRW, LST, " +
    "2021/01/29, 16:30", "bot-message",botName);