
let button = document.querySelector(".togeelChatbot");

button.addEventListener("click", () => {
  ToggleChatbot();
})

function ToggleChatbot() {
  var chatbotDivElement = document.querySelector(".chatbot");
  if (chatbotDivElement.style.display === "none") {
    chatbotDivElement.style.display = "block";
  } else {
    chatbotDivElement.style.display = "none";
  }
}