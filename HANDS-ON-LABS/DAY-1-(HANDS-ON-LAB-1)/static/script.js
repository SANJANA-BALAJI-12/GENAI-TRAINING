const chatbox = document.getElementById("chatbox");
const promptInput = document.getElementById("promptInput");
const submitBtn = document.getElementById("submitBtn");

function appendMessage(text, className) {
    const div = document.createElement("div");
    div.className = `message ${className}`;
    div.textContent = text;
    chatbox.appendChild(div);
    chatbox.scrollTop = chatbox.scrollHeight;
}

function appendStep(type, content) {
    const div = document.createElement("div");
    div.className = "step-card";
    
    const typeSpan = document.createElement("div");
    typeSpan.className = "type";
    
    // Switch color easily via inline style or CSS logic; here we'll let CSS handle base.
    if(type === 'observation') typeSpan.style.color = '#38bdf8'; // Sky blue for results
    if(type === 'action') typeSpan.style.color = '#f472b6'; // Pink for actions
    
    typeSpan.textContent = type;
    
    const contentDiv = document.createElement("div");
    contentDiv.textContent = content;
    
    div.appendChild(typeSpan);
    div.appendChild(contentDiv);
    
    chatbox.appendChild(div);
    chatbox.scrollTop = chatbox.scrollHeight;
}

function showTyping() {
    const div = document.createElement("div");
    div.className = "typing-indicator";
    div.id = "typingIndicator";
    div.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    chatbox.appendChild(div);
    chatbox.scrollTop = chatbox.scrollHeight;
}

function removeTyping() {
    const indicator = document.getElementById("typingIndicator");
    if (indicator) indicator.remove();
}

async function sendPrompt() {
    const text = promptInput.value.trim();
    if (!text) return;

    // Output User Message
    appendMessage(text, "user-message");
    promptInput.value = "";
    promptInput.disabled = true;
    submitBtn.disabled = true;

    showTyping();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt: text })
        });
        
        const data = await response.json();
        removeTyping();

        // Animate Steps sequentially
        for (const step of data.steps) {
            appendStep(step.type, step.content);
            await new Promise(r => setTimeout(r, 600)); // Delay between steps for realism
        }

        // Final answer
        if(data.final_answer) {
            appendMessage(data.final_answer, "ai-message");
        } else {
            appendMessage("I couldn't come up with an answer.", "ai-message");
        }

    } catch(err) {
        removeTyping();
        appendMessage("Sorry, an error occurred communicating with the server.", "ai-message");
    } finally {
        promptInput.disabled = false;
        submitBtn.disabled = false;
        promptInput.focus();
    }
}

submitBtn.addEventListener("click", sendPrompt);
promptInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendPrompt();
});
