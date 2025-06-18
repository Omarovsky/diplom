let socket = null;
let currentDialogId = null;
let localStream = null;
let remoteStream = null;
let pc = null;
let ws = null;
let token = "";

async function login() {
    const login = prompt("Введите логин:");
    if (!login) return alert("Логин отменён");

    const password = prompt("Введите пароль:");
    if (!password) return alert("Пароль отменён");

    try {
        const res = await fetch("http://localhost:8000/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                grant_type: "password",
                username: login,
                password: password,
                scope: "",
                client_id: "string",
                client_secret: "string"
            })
        });

        const data = await res.json();
        console.log("Response:", res.status, data);
        
        if (res.status === 200) {
            token = data.access_token;
            await fetchDialogs();
            document.getElementById("registerButton").style.display = "none";
            document.getElementById("loginButton").style.display = "none";
            alert("Логин успешно совершён!");
        } else {
            alert("Не получилось войти в аккаунт.");
        }
    } catch (error) {
        console.error("Login error:", error);
        alert("Ошибка подключения к серверу");
    }
}

async function register() {
    const username = prompt("Введите имя пользователя:");
    if (!username) return alert("Регистрация отменена");

    const fullName = prompt("Введите полное имя:");
    if (!fullName) return alert("Регистрация отменена");

    const password = prompt("Введите пароль:");
    if (!password) return alert("Регистрация отменена");

    try {
        const res = await fetch("http://localhost:8000/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                email: `${username}@coolmail.com`,
                full_name: fullName,
                password: password
            })
        });

        const data = await res.json();
        console.log("Response:", res.status, data);

        if (res.status === 200 || res.status === 201) {
            alert("Регистрация прошла успешно!");
        } else {
            alert("Ошибка регистрации: " + (data.detail || "Неизвестная ошибка"));
        }
    } catch (error) {
        console.error("Register error:", error);
        alert("Ошибка подключения к серверу");
    }
}


async function fetchDialogs() {
    if (!token) {
        const tokenInput = document.getElementById("token").value;
        if (tokenInput) {
            token = tokenInput;
        } else {
            alert("Сначала войдите в систему или введите токен");
            return;
        }
    }

    try {
        const res = await fetch("http://localhost:8000/direct/dialogs", {
            headers: { "Authorization": "Bearer " + token }
        });
        
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const dialogs = await res.json();
        const list = document.getElementById("dialogList");
        list.innerHTML = "";
        
        dialogs.forEach(dialog => {
            const btn = document.createElement("button");
            btn.textContent = "Диалог #" + dialog.id;
            btn.onclick = () => connectToDialog(dialog.id);
            list.appendChild(btn);
        });
    } catch (error) {
        console.error("Fetch dialogs error:", error);
        alert("Ошибка получения диалогов");
    }
}

async function createDialog() {
    const userId = document.getElementById("newUserId").value;
    if (!userId) return alert("Введите ID пользователя");
    if (!token) return alert("Сначала войдите в систему");

    try {
        const res = await fetch(`http://localhost:8000/direct/dialog/${userId}`, {
            method: "POST",
            headers: { "Authorization": "Bearer " + token }
        });

        const data = await res.text();
        console.log("Response:", res.status, data);

        if (res.ok) {
            await fetchDialogs();
            document.getElementById("newUserId").value = "";
            alert("Диалог создан успешно!");
        } else {
            alert("❌ Ошибка: " + res.status + " — " + data);
        }
    } catch (error) {
        console.error("Create dialog error:", error);
        alert("Ошибка создания диалога");
    }
}

// Chat functionality
async function connectToDialog(dialogId) {
    currentDialogId = dialogId;

    if (socket) {
        socket.close();
    }

    try {
        socket = new WebSocket(`ws://localhost:8000/ws-direct/${dialogId}?token=${token}`);
        
        socket.onmessage = (e) => {
            const msg = JSON.parse(e.data);
            console.log("Received message:", msg);
            
            if (msg.allmessages) {
                msg.allmessages.forEach(m => {
                    addMessage(`[${m.sender_id}] ${m.full_name}: ${m.content}`);
                });
            } else {
                addMessage(`[${msg.sender_id}] ${msg.full_name}: ${msg.content}`);
            }
        };
        
        socket.onopen = () => {
            document.getElementById("chat").innerHTML = "";
            addMessage("🟢 Подключено к диалогу #" + dialogId);
            setStatus("Подключен к диалогу #" + dialogId);
        };
        
        socket.onclose = () => {
            addMessage("🔴 Соединение с диалогом закрыто");
        };
        
        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
            addMessage("❌ Ошибка подключения к диалогу");
        };
    } catch (error) {
        console.error("Connect to dialog error:", error);
        alert("Ошибка подключения к диалогу");
    }
}

function sendMessage() {
    const input = document.getElementById("messageInput");
    const message = input.value.trim();
    
    if (!message) return;
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        alert("Сначала подключитесь к диалогу");
        return;
    }

    try {
        socket.send(JSON.stringify({ content: message }));
        input.value = "";
    } catch (error) {
        console.error("Send message error:", error);
        alert("Ошибка отправки сообщения");
    }
}

function addMessage(text) {
    console.log("Adding message:", text);
    const messageDiv = document.createElement("div");
    messageDiv.innerHTML = text;
    document.getElementById("chat").appendChild(messageDiv);
    document.getElementById("chat").scrollTop = document.getElementById("chat").scrollHeight;
}

// Video call functionality
function setStatus(msg) {
    document.getElementById('status').textContent = msg;
    console.log("Status:", msg);
}

function startCall() {
    if (!currentDialogId) {
        setStatus('Сначала выберите диалог!');
        return;
    }

    if (pc || ws) {
        setStatus('Звонок уже активен. Завершите текущий!');
        return;
    }

    try {
        ws = new WebSocket(`ws://127.0.0.1:8000/ws-webrtc/${currentDialogId}?token=${token}`);

        ws.onopen = () => setStatus('Сигнальное соединение установлено. Ожидание собеседника...');
        ws.onerror = (error) => {
            console.error("WebRTC WebSocket error:", error);
            setStatus('Ошибка WebSocket соединения');
        };
        ws.onclose = () => cleanup();

        ws.onmessage = async (event) => {
            try {
                const msg = JSON.parse(event.data);
                console.log("WebRTC message:", msg);
                
                if (msg.type === "offer") {
                    await pc.setRemoteDescription(new RTCSessionDescription(msg.offer));
                    const answer = await pc.createAnswer();
                    await pc.setLocalDescription(answer);
                    ws.send(JSON.stringify({ type: "answer", answer }));
                    setStatus('Получено приглашение. Отправлен ответ.');
                } else if (msg.type === "answer") {
                    await pc.setRemoteDescription(new RTCSessionDescription(msg.answer));
                    setStatus('Собеседник принял звонок!');
                } else if (msg.type === "ice") {
                    await pc.addIceCandidate(msg.candidate);
                }
            } catch (error) {
                console.error("WebRTC message handling error:", error);
                setStatus('Ошибка обработки сигнала');
            }
        };

        pc = new RTCPeerConnection({
            iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
        });

        pc.onicecandidate = (event) => {
            if (event.candidate && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: "ice", candidate: event.candidate }));
            }
        };

        pc.ontrack = (event) => {
            console.log("Received remote stream");
            document.getElementById('remoteVideo').srcObject = event.streams[0];
        };

        pc.onconnectionstatechange = () => {
            console.log("Connection state:", pc.connectionState);
            if (pc.connectionState === 'connected') {
                setStatus('Звонок установлен!');
            } else if (pc.connectionState === 'disconnected') {
                setStatus('Соединение потеряно');
            } else if (pc.connectionState === 'failed') {
                setStatus('Ошибка соединения');
                cleanup();
            }
        };

        navigator.mediaDevices.getUserMedia({ video: true, audio: true })
            .then(stream => {
                localStream = stream;
                document.getElementById('localVideo').srcObject = stream;
                stream.getTracks().forEach(track => pc.addTrack(track, stream));
                return pc.createOffer();
            })
            .then(offer => {
                pc.setLocalDescription(offer);
                ws.send(JSON.stringify({ type: "offer", offer }));
                setStatus('Звонок инициирован. Ожидание ответа...');
            })
            .catch(err => {
                console.error("Media access error:", err);
                setStatus("Ошибка доступа к камере/микрофону: " + err.message);
                cleanup();
            });
    } catch (error) {
        console.error("Start call error:", error);
        setStatus("Ошибка инициализации звонка");
        cleanup();
    }
}

function startScreenShare() {
    if (!pc) {
        setStatus('Сначала начните звонок!');
        return;
    }
    
    navigator.mediaDevices.getDisplayMedia({ video: true })
        .then(screenStream => {
            document.getElementById('localVideo').srcObject = screenStream;
            const videoTrack = screenStream.getVideoTracks()[0];
            const sender = pc.getSenders().find(s => s.track && s.track.kind === 'video');
            
            if (sender) {
                sender.replaceTrack(videoTrack);
            }
            
            setStatus('Демонстрация экрана началась');
            
            videoTrack.onended = () => {
                if (localStream) {
                    document.getElementById('localVideo').srcObject = localStream;
                    const camTrack = localStream.getVideoTracks()[0];
                    if (camTrack && sender) {
                        sender.replaceTrack(camTrack);
                    }
                    setStatus('Демонстрация экрана завершена');
                }
            };
        })
        .catch(err => {
            console.error("Screen share error:", err);
            setStatus("Ошибка захвата экрана: " + err.message);
        });
}

function hangUp() {
    if (ws) {
        ws.close();
        ws = null;
    }
    cleanup();
    setStatus('Звонок завершён');
}

function cleanup() {
    if (pc) {
        pc.close();
        pc = null;
    }
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
    }
    document.getElementById('localVideo').srcObject = null;
    document.getElementById('remoteVideo').srcObject = null;
    if (!document.getElementById('status').textContent.includes('завершён')) {
        setStatus('Готов к звонку');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Enter key for message input
    document.getElementById("messageInput").addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            sendMessage();
        }
    });

    document.getElementById("token").addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            fetchDialogs();
        }
    });

    document.getElementById("newUserId").addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            createDialog();
        }
    });

    setStatus('Готов к звонку');
});