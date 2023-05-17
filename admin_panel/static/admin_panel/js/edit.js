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

document.addEventListener('DOMContentLoaded', function () {
    var answer_input_elems = document.querySelectorAll('select');
    M.FormSelect.init(answer_input_elems, {});
});

var saveBtnQuestion = document.getElementById('saveBtnQuestion');
var saveBtnAnswer = document.getElementById('saveBtnAnswer');
var saveBtnContext = document.getElementById('saveBtnContext');

if (saveBtnQuestion) {
    saveBtnQuestion.onclick = function () {

        let question_text = document.getElementById('question_text').value;
        let answer_id = document.getElementById('answer').value;
        let context_id = document.getElementById('context').value;

        let data = {
            'question_text': question_text,
            'answer_id': answer_id,
            'context_id': context_id,
        }

        saveData(data);
    }
}

if (saveBtnAnswer) {
    saveBtnAnswer.onclick = function () {

        let answer_text = document.getElementById('answer_text').value;

        let data = {
            'answer_text': answer_text,
        }

        saveData(data);
    }
}

if (saveBtnContext) {
   saveBtnContext.onclick = function () {

        let context_text = document.getElementById('context_text').value;

        let data = {
            'context_text': context_text,
        }

        saveData(data);
    }
}

function saveData(data) {
    fetch('save/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(data => {
            M.toast({html: data.toast_html, classes: 'ajax_toast'})
        });
}