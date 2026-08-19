const messageList = document.getElementById("message-list");
const conversationId = messageList.dataset.conversationId;
const currentUserId = Number(messageList.dataset.currentUserId);
const messageForm = document.getElementById("message-form");
const messageError = document.getElementById("message-error");
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");


let lastMessageId = 0;

async function fetchMessages() {
    try {
        const response = await fetch(
            `/chats/${conversationId}/messages`
        );

        if (!response.ok) {
            throw new Error(
                `メッセージ取得に失敗しました: ${response.status}`
            );
        }

        const messages = await response.json();

        let hasNewMessages = false;

        for (const message of messages) {
            if (message.id <= lastMessageId) {
                continue;
            }

            const messageDiv = document.createElement("div");

            if (message.sender_id === currentUserId) {
                messageDiv.classList.add("message", "message-own", "ms-auto", "p-3", "mb-3", "rounded");
            } else {
                messageDiv.classList.add("message", "message-other", "me-auto", "p-3", "mb-3", "rounded");
            }

            const textP = document.createElement("p");
            textP.classList.add("message-text", "mb-1");
            textP.textContent = message.text;

            const timeP = document.createElement("p");
            timeP.classList.add("small", "text-body-secondary", "mb-0","text-end");
            timeP.textContent = message.created_at;

            messageDiv.appendChild(textP);
            messageDiv.appendChild(timeP);

            messageList.appendChild(messageDiv);

            lastMessageId = message.id;
            hasNewMessages = true;
        }

        if (hasNewMessages) {
            messageList.scrollTop = messageList.scrollHeight;
            await markAsRead(lastMessageId);
        }   

    } catch (error) {
        console.error("メッセージ取得エラー:", error);
    }
}

fetchMessages();

setInterval(fetchMessages, 5000);

messageForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(messageForm);

    try {
        const response = await fetch(
            `/chats/${conversationId}/messages`,
            {
                method: "POST",
                body: formData,
            }
        );

        const data = await response.json();

        if (!response.ok) {
            console.error(data);

            if (data.errors && data.errors.message) {
                messageError.textContent = data.errors.message[0];
            } else {
                messageError.textContent = "メッセージの送信に失敗しました。";
            }

            return;
        }

        messageError.textContent = "";

        messageForm.reset();
        await fetchMessages();

    } catch (error) {
        console.error(error);
        messageError.textContent =
            "通信に失敗しました。もう一度お試しください。";
    }
});

async function markAsRead(lastReadMessageId) {
    try {
        const response = await fetch(
            `/chats/${conversationId}/read`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({
                    last_read_message_id: lastReadMessageId,
                }),
            }
        );

        if (!response.ok) {
            throw new Error(
                `既読更新に失敗しました: ${response.status}`
            );
        }
    } catch (error) {
        console.error("既読更新エラー:", error);
    }
}