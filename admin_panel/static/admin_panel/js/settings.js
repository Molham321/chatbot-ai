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
    let similarity = document.getElementById('similarity').value;
    let context = document.getElementById('context').value;
    let algorithm = document.querySelector('input[name=matching-method]:checked').value;

    let data = {
        'greeting_text': greeting,
        'noanswer_text': noanswer,
        'similarity_factor': similarity,
        'context_factor': context,
        'matching_method': algorithm,
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