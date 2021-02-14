const botName = "TransportBot";
const recordTimeout = 20000;
var useTextToSpeech = Boolean(false);
var chosenVoice = null; // set on load to avoid problems with async function
var serverIp = "http://127.0.0.1:5000"
var socket = io.connect(serverIp)
var voiceList



socket.on('message', function(msg){
    addMessage(msg,"bot-message",botName)
    if (useTextToSpeech){readMessage(msg)}
})


socket.on('list', function (msg){
    var listId = Date.now()
    addMessage(msg.passed_message,"bot-message",botName,listId)
    var messageStringForSpeech = msg.passed_message
    msg.passed_list.forEach((value)=>{
        document.getElementById(listId).insertAdjacentHTML('beforeend', '<br>');
        var button = document.createElement('button')
        button.setAttribute('class','list-button')
        button.addEventListener("click", ()=>{
            inputBox = document.getElementById("message-input-box")
            inputBox.value = button.innerHTML
            submit()
        })

        messageStringForSpeech = messageStringForSpeech + ". " + value
        button.innerHTML = value
        document.getElementById(listId).appendChild(button)
    })
    document.getElementById(listId).scrollIntoView({block:"start", behavior: "smooth"})
        if (useTextToSpeech){readMessage(messageStringForSpeech)}
})


document.getElementById("message-input-box").addEventListener('keyup', function (e){
    if (e.code === 'Enter'){
        e.preventDefault();
        document.getElementById("message-submit").click();
    }
})

if ('speechSynthesis' in window){
    voiceList = speechSynthesis.getVoices();
    console.log(voiceList)
    window.speechSynthesis.onvoiceschanged=()=>{
        voiceList = speechSynthesis.getVoices();
        for (voice in voiceList){
            if (voiceList[voice]['voiceURI'] == "Google UK English Female"){
                 chosenVoice = voiceList[voice]
            }
        }
    }
}



window.addEventListener('beforeunload', function (e) {
    socket.disconnect()
});


window.addEventListener('DOMContentLoaded', ()=>{
    navigator.mediaDevices.getUserMedia({audio: true}).then(async function(stream) {
    let rtcRecorder = RecordRTC(stream, {
        type: 'audio', mimeType: 'audio/wav', recorderType: RecordRTC.StereoAudioRecorder
    });
    let rec_button = document.getElementById('record-button');
    let rec_span = document.getElementById('record-button-span');

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

    let speech_button = document.getElementById('speech-button');
    speech_button.addEventListener("click", ()=>{
        let speech_span = document.getElementById('speech-button-span');
            useTextToSpeech = !useTextToSpeech;
        if (useTextToSpeech){
            speech_span.innerHTML = 'volume_up';
        }else{
            speech_span.innerHTML = 'volume_off';
            }
    })
})



/**
 *
 * Retrieves user input-box and gets the response from the chatbot. Adds both to the chat window using addMessage
 *
 */
function submit(){
             inputBox = document.getElementById("message-input-box");
             userMessage = inputBox.value
             if (userMessage !== "") {
                 addMessage(inputBox.value, "human-message", "You")
                 socket.send(userMessage);
             }


/**
 *
 * Reads a message using text-to-speech
 *
 * @param message {string} the message to be read
 */
function readMessage(message){
        if ('speechSynthesis' in window){
            speechSynthesis.cancel()
            message = filterMessage(message);
            let speechMessage = new SpeechSynthesisUtterance(message);
            speechMessage.voice = chosenVoice;
            speechSynthesis.speak(speechMessage);

        }else{
            console.log("Browser does not support speech synthesis!")
        }



}

function filterMessage(message){      // needs changing depending how the ticket is passed to interface
    const regexHtml = /\<.*?\>/g;
    message = message.toString().replace(regexHtml,"");
    const regexLinks = /(http|https)([\S]+)/;
    console.log(message.replace(regexLinks, 'here.'));
    return message
}

/**
 *
 * Inserts a message for either the bot or the user into the chat window in the required format.
 *
 * @param message {string} the message to add to the chat
 * @param userType {string} type of user sending the message (valid inputs are "human-message" or "bot-message")
 * @param name {string} the name of the bot or user
 */
function addMessage(message, userType, name, divId = Date.now()){
    var date = new Date()
    const baseHTML = ` <div class="${userType}">
                <div class="main-message-wrapper">
                    <div class="user-message-header">
                        <div class="user-message-name">${name}</div>
                        <div class="user-message-time">${("0" + date.getHours()).slice(-2)}:${("0" + date.getMinutes()).slice(-2)}</div>
                    </div>
                    <div class="user-message-content" id=${divId}>
                        ${message}
                    </div>
                </div>
            </div>
            `;
    document.getElementById("chat-box").insertAdjacentHTML('beforeend', baseHTML);
    document.getElementById(divId).scrollIntoView({block:"start", behavior: "smooth"})
}

/**
 * Sends user audio to the server for speech recognition then puts the result into the user input-box
 * @param audio recorded user input for processing
 */
function sendAudio(audio){
    const formData = new FormData();
    formData.append('file', audio);
    response = fetch('get_audio', {
              method: 'post',
              body: formData
            }).then(function (response){
                response.json().then(function (data){
                    let wordList = data['message'];
                    if (wordList !== null){
                        document.getElementById('message-input-box').value = data['message'];
                    }
                })
            });
}

