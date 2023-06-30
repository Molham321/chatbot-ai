let webSocket;


/**
 * String which defines the bot type for message rendering.
 * @type {string}
 */
const TYPE_BOT = 'bot';

/**
 * String which defines the user type for message rendering.
 * @type {string}
 */
const TYPE_USER = 'user';


/**
 * String which defines the employee type for message rendering.
 * @type {string}
 */
const TYPE_EMPLOYEE = 'employee';


/**
 * String which defines the system type for message rendering.
 * @type {string}
 */
const TYPE_SYSTEM = 'system';

/**
 * Defines how long to wait until not typing any key counts as "not typing" in milliseconds
 * @type {number}
 */
const typingDelay = 5000;


var root = document.querySelector('html');
var messageInput = document.getElementById('actual-message');
var sendButton = document.getElementById('send-button');
var typingIndicator = document.getElementById('typing-indicator');
var typingTimer;
var isUserTyping = false

document.addEventListener("DOMContentLoaded", function (event) {

    const SESSION_TOKEN = document.getElementById('session-token').value
    const WEBSOCKET_URL = `/ws/admin/chat/${SESSION_TOKEN}/`

    let urlParts = window.location.href.split("/")

    // Attach click handler for the question submit button
    sendButton.addEventListener('click', submitMessage);
    messageInput.addEventListener('keyup', function (event) {
        if (event.code === 'Enter' && !event.shiftKey) {
            submitMessage()
            clearTimeout(typingTimer)
        }
    })

    messageInput.addEventListener('input', function () {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(function () {
            sendTypingStateToSocket(false);
        }, typingDelay);

        if (!isUserTyping) {
            sendTypingStateToSocket(true);
        }
    });

    function submitMessage() {
        var text = messageInput.value;

        if (text.length) {
            // Reset miss counter (easter egg)
            missCounter = 0;

            // Empty Input value
            messageInput.value = '';

            // Render the user message
            renderMessage(TYPE_EMPLOYEE, text);

            // Fetch question and display it
            sendRequestToSocket(text);
        }
    }

    webSocket = new WebSocket("ws://" + window.location.host + WEBSOCKET_URL);

    webSocket.onmessage = onWebSocketMessage;
})


function onWebSocketMessage(event) {
    const data = JSON.parse(event.data);

    let sender = TYPE_USER;
    let type = data.type || 'reply';

    sender = getSenderFromString(data.sender)

    if (type === 'reply') {
        renderMessage(sender, data.message);
    } else if (type === 'loading') {
        toggleProcessing(true);
    } else if (type === 'employee_joined') {
        isEmployeeConnected = true
        renderMessage(sender, data.message);
    } else if (type === 'employee_disconnected') {
        isEmployeeConnected = false
        renderMessage(sender, data.message);
    } else if (type === 'chat_history') {

        let messages = data.messages;
        for (let message of messages) {
            let currentSender = getSenderFromString(message.sender)
            let currentDate = new Date(Date.parse(message.created_at))
            renderMessage(currentSender, message.message, currentDate)
        }
    } else if (type === 'guest_disconnected') {
        renderMessage(sender, data.message)
        setTypingState(false);
        messageInput.disabled = true;
        sendButton.disabled = true;
    } else if (type === 'typing_state_changed') {
        let typingState = Boolean(data.is_typing);
        setTypingState(typingState)
    }
}

/**
 * Toggles the visibility of the typing indicator
 * @param isOtherUserTyping true, if the indicator should be visible otherwise false
 */
function setTypingState(isOtherUserTyping) {
    if (isOtherUserTyping) {
        typingIndicator.classList.remove('hidden');
    } else {
        typingIndicator.classList.add('hidden');
    }
}

function getSenderFromString(senderString) {
    if (senderString === 'bot')
        return TYPE_BOT;
    else if (senderString === 'user')
        return TYPE_USER
    else if (senderString === 'system')
        return TYPE_SYSTEM
    else if (senderString === 'employee')
        return TYPE_EMPLOYEE

    return ''
}

/**
 * Renders a message either from the user or bot perspective.
 * @param type
 * @param text
 */
function renderMessage(type, text, createdAt = new Date()) {
    var html = '';
    var history = document.getElementById('chat-history');

    if (type === TYPE_USER) {

        html = '<div class="container row">\n' +
            '\n' +
            '    <div class="container-image col s2">\n' +
            '        <img class="avatar-image" src="data:image/svg+xml,%3Csvg height=\'512pt\' viewBox=\'0 0 512 512.00019\' width=\'512pt\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'m256 511.996094c-141.484375 0-256-114.65625-256-255.996094 0-141.488281 114.496094-256 256-256 141.488281 0 255.996094 114.496094 255.996094 256 0 141.476562-114.667969 255.996094-255.996094 255.996094zm0 0\' fill=\'%2366a9df\'/%3E%3Cpath d=\'m25%0A6 0v511.996094c141.328125 0 255.996094-114.519532 255.996094-255.996094 0-141.5-114.507813-256-255.996094-256zm0 0\' fill=\'%234f84cf\'/%3E%3Cpath d=\'m256 316c-74.488281 0-145.511719 32.5625-197.417969 102.96875 103.363281 124.941406 294.6875 123.875 396.65625-2.230469-25.179687-25.046875-81.894531-100.738281-199.238281-100.738281zm0 0\' fill=\'%23d6f3fe\'/%3E%3Cpath d=\'m455.238281 416.738281c-48.140625 59.527344-120.371093 95.257813-199.238281 95.257813v-195.996094c117.347656 0 174.058594 75.699219 199.238281 100.738281zm0 0\' fill=\'%23bdecfc\'/%3E%3Cpath d=\'m256 271c-49.628906 0-90-40.375-90-90v-30c0-49.625 40.371094-90 90-90 49.625 0 90 40.375 90 90v30c0 49.625-40.375 90-90 90zm0 0\' fill=\'%23d6f3fe\'/%3E%3Cpath d=\'m256 61v210c49.628906 0 90-40.371094 90-90v-30c0-49.628906-40.371094-90-90-90zm0 0\' fill=\'%23bdecfc\'/%3E%3C/svg%3E" alt="Avatar">\n' +
            '    </div>\n' +
            '\n' +
            '    <div class="container-text col s10 z-depth-1">\n' +
            '        <p>' + text + '</p>\n' +
            '        <span class="time-right">' + getCurrentTimeFromDate(createdAt) + '</span>\n' +
            '    </div>\n' +
            '\n' +
            '</div>'
    } else if (type === TYPE_BOT) {
        html = '<div class="container row">\n' +
            '\n' +
            '    <div class="container-image col s2">\n' +
            '        <img class="avatar-image" src="data:image/svg+xml,%0A%3Csvg height=\'512pt\' viewBox=\'0 -11 512 512\' width=\'512pt\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'m501 245c0 135.308594-109.691406 245-245 245s-245-109.691406-245-245 109.691406-245 245-245 245 109.691406 245 245zm0 0\' fill=\'%2330d6ce\'/%3E%3Cpath d=\'m482 170c0 5.523438-4.476562 10-10 10s-10-4.476562-10-10c0-82.710938-67.289062-150-150-150h-112c-82.710938 0-150 67.289062-150 150 0 5.523438-4.476562 10-10 10s-10-4.476562-10-10c0-93.738281 76.261719-170 170-170h112c93.738281 0 170 76.261719 170 170zm0 0\' fill=\'%23025f80\'/%3E%3Cpath d=\'m512 147.75v40c0 16.566406-13.429688 30-30 30h-12c0 4.992188-4.476562 9.042969-10 9.042969s-10-4.050781-10-9.042969h-18c-5.523438 0-10-4.476562-10-10v-80c0-5.523438 4.476562-10 10-10h14.902344l-3.261719-8.964844c-2.832031-7.785156 1.179687-16.394531 8.964844-19.226562 7.785156-2.832032 16.390625 1.179687 19.226562 8.964844l6.996094 19.226562h3.171875c16.570312 0 30 13.433594 30 30zm-432-30h-14.902344l3.261719-8.964844c2.832031-7.785156-1.179687-16.394531-8.964844-19.226562-7.785156-2.832032-16.390625 1.179687-19.226562 8.964844l-6.996094 19.226562h-3.171875c-16.570312 0-30 13.433594-30 30v40c0 16.566406 13.429688 30 30 30h50c5.523438 0 10-4.476562 10-10v-80c0-5.523438-4.476562-10-10-10zm0 0\' fill=\'%23ff6466\'/%3E%3Cpath d=\'m482 147.75v40c0 16.566406-13.429688 30-30 30h-20c-5.523438 0-10-4.476562-10-10v-80c0-5.523438 4.476562-10 10-10h20c16.570312 0 30 13.433594 30 30zm-452 40v-40c0-12.386719 7.511719-23.015625 18.226562-27.59375.464844-.195312.773438-.644531.773438-1.148438 0-.695312-.5625-1.257812-1.253906-1.257812h-17.746094c-16.570312 0-30 13.433594-30 30v40c0 16.570312 13.429688 30 30 30h30c-16.570312 0-30-13.433594-30-30zm0 0\' fill=\'%23ff393a\'/%3E%3Cpath d=\'m286 328.75c0 22.089844-13.429688 40-30 40s-30-17.910156-30-40 13.429688-40 30-40 30 17.910156 30 40zm0 0\' fill=\'%230069a3\'/%3E%3Cpath d=\'m286 328.75c0 16.402344-7.40625 30.488281-18 36.660156-10.59375-6.171875-18-20.257812-18-36.660156s7.40625-30.488281 18-36.660156c10.59375 6.171875 18 20.257812 18 36.660156zm0 0\' fill=\'%2308c\'/%3E%3Cpath d=\'m447 173.75c0 77.320312-62.679688 140-140 140h-102c-77.320312 0-140-62.679688-140-140s62.679688-140 140-140h102c77.320312 0 140 62.679688 140 140zm-135 160h-112c-54.480469 0-101.683594 31.121094-124.820312 76.558594 44.796874 48.96875 109.21875 79.691406 180.820312 79.691406s136.023438-30.722656 180.820312-79.691406c-23.136718-45.4375-70.339843-76.558594-124.820312-76.558594zm0 0\' fill=\'%2397f0f2\'/%3E%3Cpath d=\'m307 313.75h-63.019531c-77.320313 0-140-62.679688-140-140s62.679687-140 140-140h63.019531c77.320312 0 140 62.679688 140 140s-62.679688 140-140 140zm-51 176.25c71.601562 0 136.023438-30.722656 180.820312-79.691406-23.136718-45.4375-70.339843-76.558594-124.820312-76.558594h-72c-64.859375 0-119.402344 44.105469-135.300781 103.960938 41.65625 32.753906 94.199219 52.289062 151.300781 52.289062zm0 0\' fill=\'%23c0fbff\'/%3E%3Cpath d=\'m346 444c0 10.910156-1.945312 21.359375-5.503906 31.035156-26.339844 9.679688-54.800782 13.964844-84.496094 13.964844s-58.15625-4.285156-84.496094-13.964844c-3.558594-9.675781-5.503906-20.125-5.503906-31.035156 0-49.707031 40.292969-90 90-90s90 40.292969 90 90zm0 0\' fill=\'%2308c\'/%3E%3Cpath d=\'m322 258.75h-132c-38.660156 0-70-31.339844-70-70v-30c0-38.660156 31.339844-70 70-70h132c38.660156 0 70 31.339844 70 70v30c0 38.660156-31.339844 70-70 70zm-96.984375 207.882812c-21.070313-4.699218-36.421875-23.148437-36.515625-44.738281 0-.132812 0-.261719 0-.394531 0-19.105469 5.957031-36.816406 16.109375-51.390625-23.335937 16.261719-38.609375 43.289063-38.609375 73.890625 0 10.910156 1.945312 21.359375 5.503906 31.035156 26.339844 9.679688 54.800782 14.964844 84.496094 14.964844 29.6875 0 58.136719-5.28125 84.46875-14.953125 1.355469-3.691406 2.5-7.484375 3.371094-11.386719-20.804688 5.75-42.707032 8.839844-65.339844 8.839844-18.371094 0-36.269531-2.027344-53.484375-5.867188zm0 0\' fill=\'%23006cbc\'/%3E%3Cpath d=\'m322 258.75h-102c-38.660156 0-70-31.339844-70-70v-30c0-38.660156 31.339844-70 70-70h102c38.660156 0 70 31.339844 70 70v30c0 38.660156-31.339844 70-70 70zm0 0\' fill=\'%2308c\'/%3E%3Cpath d=\'m284.285156 201.929688c3.90625 3.90625 3.90625 10.234374 0 14.140624-15.597656 15.597657-40.972656 15.597657-56.570312 0-3.902344-3.902343-3.902344-10.234374 0-14.140624 3.90625-3.90625 10.238281-3.90625 14.144531 0 7.796875 7.796874 20.484375 7.796874 28.285156 0 1.953125-1.953126 4.511719-2.929688 7.070313-2.929688s5.117187.976562 7.070312 2.929688zm-58.105468-61.234376c-15.597657-15.59375-40.976563-15.59375-56.570313 0-3.90625 3.90625-3.90625 10.238282 0 14.144532 3.90625 3.902344 10.238281 3.902344 14.144531 0 7.796875-7.800782 20.484375-7.800782 28.28125 0 1.953125 1.953125 4.511719 2.929687 7.070313 2.929687 2.558593 0 5.121093-.976562 7.074219-2.929687 3.902343-3.90625 3.902343-10.238282 0-14.144532zm116.210937 0c-15.597656-15.59375-40.972656-15.59375-56.570313 0-3.902343 3.90625-3.902343 10.238282 0 14.144532 3.90625 3.902344 10.238282 3.902344 14.144532 0 7.796875-7.800782 20.484375-7.800782 28.285156 0 1.953125 1.953125 4.511719 2.929687 7.070312 2.929687 2.558594 0 5.117188-.976562 7.070313-2.929687 3.90625-3.90625 3.90625-10.238282 0-14.144532zm0 0\' fill=\'%2330d6ce\'/%3E%3Cpath d=\'m271 437v52.546875c-4.964844.300781-9.960938.453125-15 .453125s-10.035156-.152344-15-.453125v-52.546875c0-8.285156 6.714844-15 15-15s15 6.714844 15 15zm0 0\' fill=\'%2384deea\'/%3E%3Cpath d=\'m271 437v22c0 8.285156-6.714844 15-15 15s-15-6.714844-15-15v-22c0-8.285156 6.714844-15 15-15s15 6.714844 15 15zm-15-27c9.941406 0 18-8.058594 18-18s-8.058594-18-18-18-18 8.058594-18 18 8.058594 18 18 18zm0 0\' fill=\'%23fff5f5\'/%3E%3Cpath d=\'m470 217.75v20c0 22.054688-17.945312 40-40 40h-170v-20h170c11.027344 0 20-8.972656 20-20v-20zm0 0\' fill=\'%23025f80\'/%3E%3Cpath d=\'m288.945312 283.109375h-65.890624c-9.417969 0-17.054688-7.636719-17.054688-17.054687 0-9.417969 7.636719-17.054688 17.054688-17.054688h65.890624c9.417969 0 17.054688 7.636719 17.054688 17.054688 0 9.421874-7.636719 17.054687-17.054688 17.054687zm0 0\' fill=\'%23ff6466\'/%3E%3Cpath d=\'m288.945312 283.109375h-35.890624c-9.417969 0-17.054688-7.636719-17.054688-17.054687 0-9.417969 7.636719-17.054688 17.054688-17.054688h35.890624c9.417969 0 17.054688 7.636719 17.054688 17.054688 0 9.421874-7.636719 17.054687-17.054688 17.054687zm0 0\' fill=\'%23ff895a\'/%3E%3C/svg%3E" alt="Avatar">\n' +
            '    </div>\n' +
            '\n' +
            '    <div class="container-text col s10 z-depth-1">\n' +
            '        <p>' + text + '</p>\n' +
            '        <span class="time-right">' + getCurrentTimeFromDate(createdAt) + '</span>\n' +
            '    </div>\n' +
            '\n' +
            '</div>'
    } else if (type === TYPE_EMPLOYEE) {
        html = '<div class="container bot row">\n' +
            '    <div class="container-image user col s2 push-s10">\n' +
            '        <img class="avatar-image" src="data:image/svg+xml,%3Csvg height=\'512pt\' viewBox=\'0 0 512 512.00019\' width=\'512pt\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'m256 511.996094c-141.484375 0-256-114.65625-256-255.996094 0-141.488281 114.496094-256 256-256 141.488281 0 255.996094 114.496094 255.996094 256 0 141.476562-114.667969 255.996094-255.996094 255.996094zm0 0\' fill=\'%2366a9df\'/%3E%3Cpath d=\'m25%0A6 0v511.996094c141.328125 0 255.996094-114.519532 255.996094-255.996094 0-141.5-114.507813-256-255.996094-256zm0 0\' fill=\'%234f84cf\'/%3E%3Cpath d=\'m256 316c-74.488281 0-145.511719 32.5625-197.417969 102.96875 103.363281 124.941406 294.6875 123.875 396.65625-2.230469-25.179687-25.046875-81.894531-100.738281-199.238281-100.738281zm0 0\' fill=\'%23d6f3fe\'/%3E%3Cpath d=\'m455.238281 416.738281c-48.140625 59.527344-120.371093 95.257813-199.238281 95.257813v-195.996094c117.347656 0 174.058594 75.699219 199.238281 100.738281zm0 0\' fill=\'%23bdecfc\'/%3E%3Cpath d=\'m256 271c-49.628906 0-90-40.375-90-90v-30c0-49.625 40.371094-90 90-90 49.625 0 90 40.375 90 90v30c0 49.625-40.375 90-90 90zm0 0\' fill=\'%23d6f3fe\'/%3E%3Cpath d=\'m256 61v210c49.628906 0 90-40.371094 90-90v-30c0-49.628906-40.371094-90-90-90zm0 0\' fill=\'%23bdecfc\'/%3E%3C/svg%3E" alt="Avatar">\n' +
            '    </div>\n' +
            '    <div class="container-text user col s10 pull-s2 z-depth-1">\n' +
            '        <p>' + text + '</p>\n' +
            '        <span class="time-right">' + getCurrentTimeFromDate(createdAt) + '</span>\n' +
            '    </div>\n' +
            '</div>'
    } else if (type === TYPE_SYSTEM) {
        html = '<div style="text-align: center;">' + text + '</div>';
    }

    // Append node to chatbot hsitory
    var node = document.createElement('div');
    node.innerHTML = html;
    history.appendChild(node);

    // Keep scrolled down after each new message
    scrollBottom();
}

/**
 * Scrolls the chatbot history to the bottom.
 */
function scrollBottom() {
    root.scrollTop = root.scrollHeight;
}

/**
 * Sends the ser question to the chatbot API and processes its response
 * @param _text
 */
function sendRequestToSocket(_text) {

    // Prepare POST body data
    let body = {
        'message': _text,
        'sender': 'employee'
    };

    if (!isEmployeeConnected) {
        // Activate preloading animation, if no employee is connected
        toggleProcessing(true);
    }

    webSocket.send(JSON.stringify(body));
}

/**
 * Informs the server whether the current user is typing or not
 * @param _isTyping
 */
function sendTypingStateToSocket(_isTyping) {
    isUserTyping = _isTyping;
    let body = {
        'service_message': 'typing',
        'is_typing': _isTyping,
    }

    webSocket.send(JSON.stringify(body))
}


/**
 * Returns the current Time in format HH:mm
 * @returns {string}
 */
function getCurrentTimeFromDate(time) {

    var hours = time.getHours().toString();
    var minutes = time.getMinutes().toString();

    if (minutes.length === 1) {
        minutes = '0' + minutes;
    }

    if (hours.length === 1) {
        hours = '0' + hours;
    }

    return hours + ':' + minutes;
}