const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

function addMessage(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message');
    if (sender === 'user') {
        messageDiv.classList.add('user-message');
        messageDiv.textContent = message; 
    } else {
        messageDiv.classList.add('bot-message');
        messageDiv.innerHTML = `<strong>LLM Bot</strong>${message}`;
    }
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('loading-indicator');
    loadingDiv.id = 'loading'; 
    loadingDiv.textContent = 'LLM 思考中...';
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function hideLoading() {
    const loadingDiv = document.getElementById('loading');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}


async function sendMessage() {
    const message = userInput.value.trim();
    if (message === '') return; 

    addMessage(message, 'user');
    userInput.value = ''; 
    sendButton.disabled = true; 
    showLoading(); 

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        });

        hideLoading(); 

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: '無法解析錯誤訊息' }));
            console.error("伺服器錯誤:", response.status, errorData);
            addMessage(`錯誤：${errorData.error || '與伺服器通訊失敗'}`, 'bot');
            return;
        }

        const data = await response.json();

        if (data.response) {
            addMessage(data.response, 'bot');
        } else if (data.error) {
             console.error("後端處理錯誤:", data.error);
             addMessage(`後端錯誤：${data.error}`, 'bot');
        }

    } catch (error) {
        hideLoading();
        console.error('發送訊息時出錯:', error);
        addMessage('糟糕，無法連接到伺服器！請檢查網路連線或稍後再試。', 'bot');
    } finally {
         sendButton.disabled = false; 
         userInput.focus();
    }
}

sendButton.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

userInput.focus();