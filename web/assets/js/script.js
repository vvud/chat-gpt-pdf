const loader = `<span class='loader'><span class='loader__dot'></span><span class='loader__dot'></span><span class='loader__dot'></span></span>`
const errorMessage = 'I\'m not avail at the moment, however, feel free to call our support team directly 0123456789.'
const urlPattern = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim
const $document = document
const $chatbot = $document.querySelector('.chatbot')
const $conversationContainer = $document.querySelector('.conversation-container')
const $conversation = $document.querySelector('.conversation')
const $chatbotInput = $document.querySelector('.question-input')
const $chatbotSubmit = $document.querySelector('.question-submit')

const botLoadingDelay = 500
const botReplyDelay = 0

document.addEventListener('keypress', event => {
    if (event.which == 13) validateMessage()
}, false)

$chatbotSubmit.addEventListener('click', () => {
    validateMessage()
}, false)

const toggle = (element, klass) => {
    const classes = element.className.match(/\S+/g) || [],
        index = classes.indexOf(klass)
    index >= 0 ? classes.splice(index, 1) : classes.push(klass)
    element.className = classes.join(' ')
}

const userMessage = content => {
    let currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: "2-digit" });
    $conversation.innerHTML += `<div class="chatbot-message user-message animation"><p class="chatbot-text" senttime="${currentTime}">${content}</p></div>`
}

const aiMessage = (content, isLoading = false, delay = 0) => {
setTimeout(() => {
    removeLoader()
    let currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: "2-digit" });
    $conversation.innerHTML += `<div class="chatbot-message chatbot animation" id='${isLoading ? "is-loading" : ""}'>
        <div class="chatbot-text" senttime="${currentTime}">${content.replace(/\n\n/g, '<br>').replace(/\n/g, '<br>')}</div>
    </div>`
    scrollDown()
}, delay)
}

const removeLoader = () => {
    let loadingElem = document.getElementById('is-loading')
    if (loadingElem) $conversation.removeChild(loadingElem)
}

const escapeScript = unsafe => {
    const safeString = unsafe
        .replace(/</g, ' ')
        .replace(/>/g, ' ')
        .replace(/&/g, ' ')
        .replace(/"/g, ' ')
        .replace(/\\/, ' ')
        .replace(/\s+/g, ' ')
    return safeString.trim()
}

const validateMessage = () => {
    const text = $chatbotInput.value
    const safeText = text ? escapeScript(text) : ''
    if (safeText.length && safeText !== ' ') {
        resetInputField()
        userMessage(safeText)
        send(safeText)
    }
    scrollDown()
    return
}

const setResponse = (val, delay = 0) => {
    setTimeout(() => {
        aiMessage(val)
    }, delay)
}

const resetInputField = () => {
    $chatbotInput.value = ''
}

const scrollDown = () => {
    const distanceToScroll =
        $conversationContainer.scrollHeight -
        ($conversation.lastChild.offsetHeight + 60)
    $conversationContainer.scrollTop = distanceToScroll
    return false
}

const token = 'api-demo'
const send = (text = '') => {
    fetch('/api/chat/response', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({question: text})
    })
    .then(response => response.json())
    .then(res => {
        if (res.status < 200 || res.status >= 300) {
            let error = new Error(res.statusText)
            throw error
        }
        return res
    })
    .then(res => {
        setResponse(res.data, botLoadingDelay + botReplyDelay)
    })
    .catch(error => {
        setResponse(errorMessage, botLoadingDelay + botReplyDelay)
        resetInputField()
        console.log(error)
    })

    aiMessage(loader, true, botLoadingDelay)
}

function checkAccess() {
    var accessGranted = sessionStorage.getItem('access_granted');
    return accessGranted === 'true';
}

function addClassIfNotGranted() {
    if (!checkAccess()) {
        document.body.classList.add('validate-access');
    }
}

document.addEventListener('DOMContentLoaded', addClassIfNotGranted);

function checkKeyPress(event) {
    if (event.which == 13) {
        submitAccessCode();
    }
}

function submitAccessCode() {
    var accessCode = $document.querySelector('#access-code').value;  
    // Send post request to api
    fetch('/api/code/verify', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({access_code: accessCode})
    })
    .then(response => response.json()) // Parse response to JSON
    .then(data => {
        if (data === true) {
            sessionStorage.setItem('access_granted', true);
            // document.body.classList.remove('validate-access');
            location.reload();
        } else {
            $document.querySelector('#access-code').value = ''
            alert('Access denied');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
  
