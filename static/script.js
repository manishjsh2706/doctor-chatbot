function sendMessage() {
    const input = document.getElementById("userInput");
    const message = input.value;
    input.value = "";

    appendMessage("user", message);

    fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: message})
    }).then(res => {
        if (!res.ok) throw new Error("Network response was not ok");
        return res.json();
    })
    .then(data => appendMessage("bot", data.reply))
    .catch(err => {
        console.error("Error:", err);
        appendMessage("bot", "Error: Could not connect to the server.");
    });
}

function appendMessage(sender, text) {
    const box = document.getElementById("chatbox");
    const msg = document.createElement("p");
    msg.className = sender;
    msg.innerText = text;
    box.appendChild(msg);
    box.scrollTop = box.scrollHeight;
}
