
let button = document.querySelector(".togeelChatbot");

button.addEventListener("click", () => {
  ToggleChatbot();
})

// Initialisierung der Variablen, um das iframe-Element zu speichern
var iframe = null;

function ToggleChatbot() {
  var chatbotDivElement = document.querySelector(".chatbot");

  if (!iframe) {
    // Erstellen des iframe-Elements, wenn es noch nicht existiert
    iframe = document.createElement('iframe');
    iframe.src = "http://127.0.0.1:8000/chatbot/";
    iframe.width = "100%";
    iframe.height = "90%";
    iframe.style.border = "1px solid lightgray";
    iframe.name = "Test";

    chatbotDivElement.appendChild(iframe);
  }

  // Umschalten der Sichtbarkeit des iframe-Elements
  if (chatbotDivElement.style.display === "block") {
    chatbotDivElement.style.display = "none";
  } else {
    chatbotDivElement.style.display = "block";
  }
}