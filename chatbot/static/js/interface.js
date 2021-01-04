

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
                    console.log(data);
                    // take response here
                    addMessage(data.message, "bot-message", "TransportBot")
                })
            });
            inputBox.value = "";
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
document.getElementById("message-input-box").addEventListener('keyup', function (e){
    if (e.code === 'Enter'){
        e.preventDefault();
        document.getElementById("message-submit").click();
    }
})
addMessage("Hello! Let me know what I can help you with.", "bot-message","TransportBot");
addMessage("For testing, try giving me a message in the following format: CRS1, CRS2, date, time. e.g.: NRW, LST, " +
    "2021/01/29, 16:30", "bot-message","TransportBot");