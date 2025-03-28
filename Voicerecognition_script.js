function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;

    let chatBox = document.getElementById("chat-box");

    // Display user message
    let userMessage = document.createElement("div");
    userMessage.className = "message user";
    userMessage.innerText = userInput;
    chatBox.appendChild(userMessage);
    
    // Send to Flask backend
    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        // Display bot message
        let botMessage = document.createElement("div");
        botMessage.className = "message bot";
        botMessage.innerText = data.response;
        chatBox.appendChild(botMessage);

        // Play voice response
        let audio = new Audio(data.audio);
        audio.play();

        // Scroll chat to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    });

    // Clear input field
    document.getElementById("user-input").value = "";
}
