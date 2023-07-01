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
    var elems = document.querySelectorAll('.collapsible');
    var instances = M.Collapsible.init(elems, {});
});

saveBtn = document.getElementById('saveBtn');
saveBtn.onclick = function () {

    let greeting = document.getElementById('greeting').value;
    let noanswer = document.getElementById('no-answer').value;
    let employeeJoined = document.getElementById('employee-joined').value;
    let employeeLeft = document.getElementById('employee-left').value;
    let userLeft = document.getElementById('user-left').value;

    let similarity = document.getElementById('similarity').value;
    let context = document.getElementById('context').value;
    let algorithm = document.querySelector('input[name=matching-method]:checked').value;

    let mailTimeout = document.getElementById('mail-timeout').value;
    let similarityThreshold = document.getElementById('similarity-threshold').value;
    let qualityTestAnswers = document.getElementById('quality-test-answers').value;

    let mailRequestText = document.getElementById('mail-request-text').value;
    let mailSentText = document.getElementById('mail-sent-text').value;
    let mailInputText = document.getElementById('mail-input-text').value;
    let mailInvalidInputText = document.getElementById('mail-invalid-input-text').value;
    let mailCancelText = document.getElementById('mail-cancel-text').value;

    let data = {
        'greeting_text': greeting,
        'noanswer_text': noanswer,
        'employee_joined_text': employeeJoined,
        'employee_left_text': employeeLeft,
        'user_left_text': userLeft,
        'similarity_factor': similarity,
        'context_factor': context,
        'matching_method': algorithm,
        'mail_timeout': mailTimeout,
        'similarity_threshold': similarityThreshold,
        'quality_test_answers': qualityTestAnswers,
        'mail_request_text': mailRequestText,
        'mail_sent_text': mailSentText,
        'mail_input_text': mailInputText,
        'mail_invalid_input_text': mailInvalidInputText,
        'mail_cancel_text': mailCancelText,
    }

    console.log(data);

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