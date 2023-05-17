function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
const TYPE_QUESTION = 'question';
const TYPE_ANSWER = 'answer';

document.addEventListener('DOMContentLoaded', function () {
    var tab_el = document.querySelectorAll('.tabs');
    M.Tabs.init(tab_el, {});

    var toggleButtons = document.querySelectorAll('.toggle-button');

    toggleButtons.forEach(function (element) {
        element.addEventListener('click', function (event) {
            var type = event.currentTarget.getAttribute('data-type');
            var id = event.currentTarget.getAttribute('data-id');
            var requestUrl = 'toggle/';

            var data = {
                'id': id,
                'type': type
            }

            if (requestUrl) {
                fetch(requestUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    },
                    body: JSON.stringify(data),
                })
                    .then(response => response.json())
                    .then(data => {

                        var sender = document.querySelector('.toggle-button[data-id="' + data.id + '"][data-type="' + type + '"]');

                        if (data.status === true) {
                            sender.classList.add('active');
                            sender.setAttribute('title', 'Aktiv');
                        } else if (data.status === false) {
                            sender.classList.remove('active');
                            sender.setAttribute('title', 'Inaktiv');
                        }

                        M.toast({html: data.toast_html, classes: 'ajax_toast'})
                    });
            }

        });
    });


});



