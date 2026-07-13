const chatContainer = document.getElementById("chat-container");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

const attachBtn = document.getElementById("attach-btn");
const fileInput = document.getElementById("file-input");
const fileIndicator = document.getElementById("file-indicator");
const fileNameSpan = document.getElementById("file-name");
const removeFileBtn = document.getElementById("remove-file-btn");

let selectedFile = null;

// Handle file selection
attachBtn.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        fileNameSpan.textContent = selectedFile.name;
        fileIndicator.classList.remove("hidden");
    }
});

removeFileBtn.addEventListener("click", () => {
    selectedFile = null;
    fileInput.value = "";
    fileIndicator.classList.add("hidden");
});

// Handle entering text
userInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener("click", sendMessage);

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text && !selectedFile) return;

    // Remove user input
    userInput.value = "";
    
    // Create form data
    const formData = new FormData();
    formData.append("message", text || "Lütfen bu dosyayı incele.");
    if (selectedFile) {
        formData.append("file", selectedFile);
        appendMessage("user", text + `\n\n*(📎 ${selectedFile.name} eklendi)*`);
    } else {
        appendMessage("user", text);
    }
    
    // Clear selection UI
    selectedFile = null;
    fileInput.value = "";
    fileIndicator.classList.add("hidden");

    // Append temporary Bot Message
    const loadingId = "loading-" + Date.now();
    appendMessage("bot", '<div class="animate-pulse flex space-x-2"><div class="w-2 h-2 bg-blue-400 rounded-full"></div><div class="w-2 h-2 bg-blue-400 rounded-full"></div><div class="w-2 h-2 bg-blue-400 rounded-full"></div></div>', loadingId);

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            body: formData // Note: omitting Content-Type so browser sets it with boundary for multipart/form-data
        });
        
        const data = await response.json();
        const loadingDiv = document.getElementById(loadingId);
        
        if (loadingDiv) {
            loadingDiv.outerHTML = formatBotResponse(data.reply);
        } else {
             appendMessage("bot", formatBotResponse(data.reply));
        }

        // Render Math and Mermaid
        await renderExtensions();
        
    } catch (error) {
        document.getElementById(loadingId).innerText = "Hata oluştu. Sunucuya bağlanılamadı.";
    }
}

function appendMessage(sender, content, id = null) {
    const div = document.createElement("div");
    div.className = `p-5 rounded-lg shadow-lg ${sender === "user" ? "msg-user self-end ml-16" : "msg-bot mr-16"}`;
    if (id) div.id = id;
    
    if (sender === "user") {
        div.innerText = content;
    } else {
        div.innerHTML = content;
    }
    
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return div;
}

function formatBotResponse(markdownText) {
    let parsedHTML = marked.parse(markdownText);
    return `<div class="bot-content">${parsedHTML}</div>`;
}

function sanitizeMermaidCode(code) {
    // Replace unquoted labels in brackets: node_id[label] -> node_id["label"]
    code = code.replace(/([a-zA-Z0-9_-]+)\[([^"\n\]]+)\]/g, (match, id, label) => {
        return `${id}["${label.trim()}"]`;
    });
    
    // Replace unquoted labels in parentheses: node_id(label) -> node_id("label")
    code = code.replace(/([a-zA-Z0-9_-]+)\(([^"\n\)]+)\)/g, (match, id, label) => {
        if (label.startsWith('(') || label.endsWith(')')) {
            return match;
        }
        return `${id}("${label.trim()}")`;
    });
    
    // Replace unquoted labels in double parentheses: node_id((label)) -> node_id(("label"))
    code = code.replace(/([a-zA-Z0-9_-]+)\(\(([^"\n\)]+)\)\)/g, (match, id, label) => {
        return `${id}(("${label.trim()}"))`;
    });

    // Replace unquoted labels in curly braces: node_id{label} -> node_id{"label"}
    code = code.replace(/([a-zA-Z0-9_-]+)\{([^"\n\}]+)\}/g, (match, id, label) => {
        return `${id}{"${label.trim()}"}`;
    });

    // Replace unquoted labels in flag shapes: node_id>label] -> node_id>"label"]
    code = code.replace(/([a-zA-Z0-9_-]+)\>([^"\n\]]+)\]/g, (match, id, label) => {
        return `${id}>"${label.trim()}"]`;
    });

    return code;
}

async function renderExtensions() {
    // 1. Math Rendering
    renderMathInElement(chatContainer, {
        delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '$', right: '$', display: false},
            {left: '\\(', right: '\\)', display: false},
            {left: '\\[', right: '\\]', display: true}
        ],
        throwOnError: false
    });

    // 2. Mermaid Rendering
    const mermaidNodes = document.querySelectorAll('.language-mermaid');
    for (let i = 0; i < mermaidNodes.length; i++) {
        const el = mermaidNodes[i];
        if (el.getAttribute('data-processed')) continue;
        el.setAttribute('data-processed', 'true');
        
        let code = el.textContent.trim();
        let sanitized = sanitizeMermaidCode(code);
        
        const id = 'mermaid-render-' + Date.now() + '-' + i;
        try {
            const { svg } = await window.mermaid.render(id, sanitized);
            const preEl = el.parentElement;
            if (preEl) {
                preEl.innerHTML = svg;
            }
        } catch (err) {
            console.error("Mermaid rendering error for node:", err);
            const preEl = el.parentElement;
            if (preEl) {
                preEl.innerHTML = `
                    <div class="p-3 bg-red-900/20 border border-red-500/30 rounded text-xs text-red-300 mb-2">
                        ⚠️ Diyagram çizilirken hata oluştu. Ham veri gösteriliyor:
                    </div>
                    <pre class="bg-slate-800 p-3 rounded overflow-x-auto text-xs text-slate-300 font-mono">${code}</pre>
                `;
            }
            const badEl = document.getElementById('d' + id);
            if (badEl) badEl.remove();
        }
    }
}
