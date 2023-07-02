document.addEventListener("DOMContentLoaded", function (event) {
        const WEBSOCKET_URL = "/ws/admin/chats/";
        const SESSION_URL = "/chatbot/instantiate_session/"
        const AUTO_JOIN_TIMEOUT = 50000;

        /**
         * API Key used for API fetches
         * @type {string}
         */
        const API_KEY = 'Token d56f72fab5d730a9fe15952c035d38c053f9b757';

        const sessionList = document.getElementById("session-list");
        const autoConnectToggle = document.getElementById('auto-connect-toggle');

        var connectAutomaticallyToNewChat = false;
        var sessionToken;
        var autoJoinTimeout;
        var isAutoJoinTimeoutActive = false;

        var socket
        var requestedChats = []

        instantiateSession()
            .then((session) => {

                sessionToken = session.token;

                socket = new WebSocket("ws://" + window.location.host + WEBSOCKET_URL);
                socket.onmessage = onSocketMessage;
            })


        function onSocketMessage(event) {
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
            } else if (data.event === "join_request_answer") {
                handleJoinRequestAnswer(data.requestor_session_token, data.chat_session_token);
            }
        }

        autoConnectToggle.addEventListener('change', function () {
            connectAutomaticallyToNewChat = autoConnectToggle.checked
        });

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

            if (autoConnectToggle.checked && !isAutoJoinTimeoutActive) {
                sendJoinRequest(session.session_token);
            }
        }

        function startAutoJoinTimeout() {
            if (autoJoinTimeout) {
                clearTimeout(autoJoinTimeout);
            }

            isAutoJoinTimeoutActive = true;

            autoJoinTimeout = setTimeout(function () {
                isAutoJoinTimeoutActive = false;
            }, AUTO_JOIN_TIMEOUT);
        }

        function sendJoinRequest(chatSessionToken) {
            var body = {
                'event': 'join_request',
                'requestor_session_token': sessionToken,
                'chat_session_token': chatSessionToken
            };

            addRequestedChatToken(chatSessionToken);

            socket.send(JSON.stringify(body));
        }

        function handleJoinRequestAnswer(joinRequestorToken, chatSessionToken) {
            if (joinRequestorToken === sessionToken && isChatRequested(chatSessionToken)) {
                var url = "/adminpanel/chat/" + chatSessionToken;
                var newTab = window.open(url, "_blank");

                startAutoJoinTimeout()
            }

            removeRequestedChat(chatSessionToken);
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


        function instantiateSession() {
            return new Promise((resolve) => {
                fetch(SESSION_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': API_KEY,
                    }
                }).then(function (response) {
                    if (response.ok) {
                        return response.json();
                    }
                }).then(data => resolve(data))
            })
        }

        function addRequestedChatToken(chatSessionToken) {
            requestedChats.push(chatSessionToken)
        }

        function removeRequestedChat(chatSessionToken) {
            const index = requestedChats.indexOf(chatSessionToken)
            if (index !== -1) {
                requestedChats.splice(index, 1);
            }
        }

        function isChatRequested(chatSessionToken) {
            return requestedChats.includes(chatSessionToken);
        }
    }
)
