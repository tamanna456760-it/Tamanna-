document.getElementById("input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    let msg = e.target.value;
    let chat = document.getElementById("chat-box");
    chat.innerHTML += "<p>You: " + msg + "</p>";
    e.target.value = "";
  }
});
