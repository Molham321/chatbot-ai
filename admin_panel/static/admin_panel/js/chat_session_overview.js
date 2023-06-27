document.addEventListener("DOMContentLoaded", function (event) {
    const WEBSOCKET_URL = "/ws/admin/chats/";
    const sessionList = document.getElementById("session-list");

    const socket = new WebSocket("ws://" + window.location.host + WEBSOCKET_URL);

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.event === "active_sessions") {
            updateSessionList(data.sessions);
        } else if (data.event === "new_chat_session_notification") {
            handleNewChatSession(data.session);
        } else if (data.event === "chat_session_ended_notification") {
            handleChatSessionEnded(data.session_token);
        } else if (data.event === "employee_joined_notification") {
            handleEmployeeJoinedChat(data.session_token);
        } else if (data.event === "employee_left_notification") {
            handleEmployeeLeftChat(data.session_token);
        }
    };

    function updateSessionList(sessions) {
        sessionList.innerHTML = "";

        for (let i = 0; i < sessions.length; i++) {
            const session = sessions[i];

            addNewSessionLink(session)
        }
    }

    function addNewSessionLink(session) {
        const sessionItem = document.createElement("div");
        sessionItem.classList.add("session-item", "card-panel");
        sessionItem.innerText = session.initial_message;

        sessionItem.setAttribute("data-session-token", session.session_token);

        if (session.is_employee_present) {
            const icon = document.createElement("i");
            icon.classList.add("material-icons", "right");
            icon.innerText = "person";

            sessionItem.appendChild(icon);
        }

        if (!session.is_ended) {
            let sessionElement;

            if (session.is_employee_present) {
                sessionElement = document.createElement("div");
                sessionElement.classList.add("session-link-disabled");
            } else {
                sessionElement = document.createElement("a");
                sessionElement.href = "/adminpanel/chat/" + session.session_token;
            }

            sessionElement.classList.add("session-link");
            sessionElement.appendChild(sessionItem);
            sessionList.appendChild(sessionElement);
        } else {
            sessionItem.classList.add("session-item-ended");
            sessionList.appendChild(sessionItem);
        }
    }

    function handleNewChatSession(session) {
        addNewSessionLink(session)
    }

    function handleChatSessionEnded(sessionToken) {
        const sessionItem = sessionList.querySelector(
            ".session-item[data-session-token='" + sessionToken + "']"
        );

        if (sessionItem) {
            sessionItem.remove();
        }
    }

    function handleEmployeeJoinedChat(sessionToken) {
        const sessionItem = sessionList.querySelector(
            ".session-item[data-session-token='" + sessionToken + "']"
        );

        if (sessionItem) {
            const icon = document.createElement("i");
            icon.classList.add("material-icons", "right");
            icon.innerText = "person";

            sessionItem.appendChild(icon);

            const sessionLink = sessionItem.parentNode;
            const sessionLinkReplacement = document.createElement("div");
            sessionLinkReplacement.classList.add("session-link-disabled");
            sessionLinkReplacement.appendChild(sessionItem.cloneNode(true));

            sessionLink.parentNode.replaceChild(sessionLinkReplacement, sessionLink);
        }
    }

    function handleEmployeeLeftChat(sessionToken) {
        const sessionItem = sessionList.querySelector(
            ".session-item[data-session-token='" + sessionToken + "']"
        );

        if (sessionItem) {
            const icon = sessionItem.querySelector("i");

            if (icon) {
                icon.remove();
            }

            const sessionLinkReplacement = sessionItem.parentNode;
            const sessionLink = document.createElement("a");
            sessionLink.classList.add("session-link");
            sessionLink.href = "/adminpanel/chat/" + sessionToken;
            sessionLink.appendChild(sessionItem.cloneNode(true));

            sessionLinkReplacement.parentNode.replaceChild(sessionLink, sessionLinkReplacement);
        }
    }


});