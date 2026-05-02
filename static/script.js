function sendMessage() {
    const input = document.getElementById("userInput");
    const message = input.value;
    input.value = "";

    appendMessage("user", message);

    fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: message})
    })
    .then(res => res.json())
    .then(data => appendMessage("bot", data.reply));
}

function appendMessage(sender, text) {
    const box = document.getElementById("chatbox");
    const msg = document.createElement("p");
    msg.className = sender;
    msg.innerText = text;
    box.appendChild(msg);
    box.scrollTop = box.scrollHeight;
}
