import asyncio
import json
from typing import Any, Callable, Coroutine
from aiohttp import web

AVATAR_HTML = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Aether — Otonom İnsansı Avatar</title>
<style>
  :root {
    --bg: #0b0f17;
    --panel: #131b2b;
    --border: #24324d;
    --text: #e8eef9;
    --muted: #93a4c3;
    --accent: #5b8cff;
    --accent2: #22d3ee;
  }
  * { box-sizing: border-box; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
  body { margin: 0; background: var(--bg); color: var(--text); min-height: 100vh; display: flex; flex-direction: column; }
  header { padding: 14px 22px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; background: #0e1420; }
  .badge { font-size: 12px; padding: 4px 10px; border-radius: 999px; background: rgba(91,140,255,0.15); color: var(--accent2); border: 1px solid rgba(34,211,238,0.3); }
  main { display: grid; grid-template-columns: 380px 1fr; gap: 18px; padding: 18px; max-width: 1360px; width: 100%; margin: 0 auto; flex: 1; }
  @media (max-width: 920px) { main { grid-template-columns: 1fr; } }
  .card { background: var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
  .avatar-stage { display: flex; flex-direction: column; align-items: center; gap: 8px; }
  svg#humanAvatar { width: 250px; height: 290px; filter: drop-shadow(0 12px 30px rgba(34,211,238,0.12)); }
  .chat-box { flex: 1; min-height: 260px; max-height: 360px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding-right: 4px; }
  .msg { padding: 10px 14px; border-radius: 12px; max-width: 82%; line-height: 1.45; font-size: 14px; }
  .msg.user { align-self: flex-end; background: var(--accent); color: #fff; }
  .msg.assistant { align-self: flex-start; background: #1c273d; border: 1px solid var(--border); }
  .controls { display: flex; gap: 8px; }
  input[type="text"] { flex: 1; padding: 11px 14px; border-radius: 10px; border: 1px solid var(--border); background: #0c121d; color: var(--text); outline: none; }
  button { padding: 10px 15px; border-radius: 10px; border: none; background: var(--accent); color: #fff; font-weight: 600; cursor: pointer; }
  button.secondary { background: #1e2b45; border: 1px solid var(--border); }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  pre { margin: 0; font-size: 12px; color: var(--muted); white-space: pre-wrap; max-height: 170px; overflow-y: auto; background: #0d131f; padding: 10px; border-radius: 10px; }
  .small { font-size: 12px; color: var(--muted); }
</style>
</head>
<body>
  <header>
    <div><strong>AETHER</strong> <span class="small">Otonom İnsansı Avatar &amp; Zekâ Sistemi</span></div>
    <span class="badge" id="emotionBadge">Duygu: neutral</span>
  </header>
  <main>
    <section class="card avatar-stage">
      <svg id="humanAvatar" viewBox="0 0 260 300">
        <defs>
          <linearGradient id="skinGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#f3c6a5" />
            <stop offset="100%" stop-color="#dfa37c" />
          </linearGradient>
          <linearGradient id="hairGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#293548" />
            <stop offset="100%" stop-color="#111827" />
          </linearGradient>
        </defs>
        <!-- Omuzlar ve Yaka -->
        <path d="M40 290 C45 232, 85 215, 130 215 C175 215, 215 232, 220 290 Z" fill="#1e293b" stroke="#334155" stroke-width="2"/>
        <path d="M104 217 L130 256 L156 217" fill="none" stroke="#22d3ee" stroke-width="2.5"/>
        <!-- Boyun -->
        <rect x="112" y="182" width="36" height="42" rx="14" fill="url(#skinGrad)"/>
        <!-- Kulaklar -->
        <ellipse cx="66" cy="132" rx="10" ry="18" fill="#e2a882"/>
        <ellipse cx="194" cy="132" rx="10" ry="18" fill="#e2a882"/>
        <!-- Baş -->
        <path d="M72 115 C72 62, 188 62, 188 115 C188 168, 164 198, 130 198 C96 198, 72 168, 72 115 Z" fill="url(#skinGrad)"/>
        <!-- Saç -->
        <path d="M70 112 C68 50, 192 46, 190 112 C182 82, 155 72, 130 74 C102 76, 80 86, 70 112 Z" fill="url(#hairGrad)"/>
        <!-- Kaşlar -->
        <path id="browL" d="M88 106 Q104 98 118 105" fill="none" stroke="#293548" stroke-width="3.5" stroke-linecap="round"/>
        <path id="browR" d="M142 105 Q156 98 172 106" fill="none" stroke="#293548" stroke-width="3.5" stroke-linecap="round"/>
        <!-- Gözler -->
        <g id="eyeL">
          <ellipse cx="103" cy="120" rx="12" ry="7.5" fill="#ffffff"/>
          <circle cx="103" cy="120" r="4.5" fill="#1e293b"/>
          <circle cx="101.5" cy="118.5" r="1.5" fill="#ffffff"/>
        </g>
        <g id="eyeR">
          <ellipse cx="157" cy="120" rx="12" ry="7.5" fill="#ffffff"/>
          <circle cx="157" cy="120" r="4.5" fill="#1e293b"/>
          <circle cx="155.5" cy="118.5" r="1.5" fill="#ffffff"/>
        </g>
        <!-- Burun -->
        <path d="M130 118 L126 142 L135 145" fill="none" stroke="#b97b56" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
        <!-- Ağız (Konuşma & Duygu) -->
        <path id="mouth" d="M108 165 Q130 174 152 165" fill="#9f4a4a" stroke="#7f1d1d" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <div class="small" id="statusText">Çevrimiçi ve otonom döngü aktif</div>
      <div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:center;">
        <button class="secondary" onclick="triggerCycle()">Otonom Döngü Çalıştır</button>
        <button class="secondary" onclick="toggleVoice()">Sesli Okuma: Açık</button>
      </div>
    </section>

    <section style="display:flex; flex-direction:column; gap:14px;">
      <div class="card">
        <strong>Avatar ile Sohbet</strong>
        <div class="chat-box" id="chatBox"></div>
        <div class="controls">
          <input id="chatInput" type="text" placeholder="Avatarla konuş, fikir sor veya otonom yönlendirme ver..." onkeydown="if(event.key==='Enter') sendChat()" />
          <button onclick="sendChat()">Gönder</button>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <strong>Otonom Beyin &amp; Kararlar</strong>
          <pre id="brainBox">Yükleniyor...</pre>
        </div>
        <div class="card">
          <strong>Öz-Gelişim &amp; Hafıza</strong>
          <pre id="memoryBox">Yükleniyor...</pre>
        </div>
      </div>
    </section>
  </main>

<script>
let voiceEnabled = true;
let speakingTimer = null;

function setEmotion(emotion) {
  document.getElementById("emotionBadge").textContent = "Duygu: " + emotion;
  const browL = document.getElementById("browL");
  const browR = document.getElementById("browR");
  if (emotion === "happy") {
    browL.setAttribute("d", "M88 102 Q104 94 118 102");
    browR.setAttribute("d", "M142 102 Q156 94 172 102");
  } else if (emotion === "surprised" || emotion === "curious") {
    browL.setAttribute("d", "M88 97 Q104 88 118 99");
    browR.setAttribute("d", "M142 99 Q156 88 172 97");
  } else if (emotion === "sad" || emotion === "thinking") {
    browL.setAttribute("d", "M88 109 Q104 102 118 104");
    browR.setAttribute("d", "M142 104 Q156 102 172 109");
  } else {
    browL.setAttribute("d", "M88 106 Q104 98 118 105");
    browR.setAttribute("d", "M142 105 Q156 98 172 106");
  }
}

function animateMouth(visemes, text) {
  const mouth = document.getElementById("mouth");
  if (speakingTimer) clearInterval(speakingTimer);
  if (voiceEnabled && "speechSynthesis" in window && text) {
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "tr-TR";
    window.speechSynthesis.speak(utter);
  }
  let idx = 0;
  speakingTimer = setInterval(() => {
    if (!visemes || idx >= visemes.length) {
      clearInterval(speakingTimer);
      mouth.setAttribute("d", "M110 166 Q130 173 150 166");
      return;
    }
    const v = visemes[idx++].viseme;
    if (v === "AA" || v === "O" || v === "U") {
      mouth.setAttribute("d", "M116 163 Q130 183 144 163 Q130 158 116 163 Z");
    } else if (v === "E" || v === "IH") {
      mouth.setAttribute("d", "M110 165 Q130 175 150 165 Q130 169 110 165 Z");
    } else if (v === "MBP" || v === "FV") {
      mouth.setAttribute("d", "M112 167 L148 167");
    } else {
      mouth.setAttribute("d", "M110 166 Q130 173 150 166");
    }
  }, 85);
}

setInterval(() => {
  const eyeL = document.getElementById("eyeL");
  const eyeR = document.getElementById("eyeR");
  eyeL.setAttribute("transform", "scale(1, 0.12) translate(0, 1050)");
  eyeR.setAttribute("transform", "scale(1, 0.12) translate(0, 1050)");
  setTimeout(() => {
    eyeL.removeAttribute("transform");
    eyeR.removeAttribute("transform");
  }, 140);
}, 3800);

function appendMsg(role, text) {
  const box = document.getElementById("chatBox");
  const div = document.createElement("div");
  div.className = "msg " + role;
  div.textContent = text;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

function toggleVoice() {
  voiceEnabled = !voiceEnabled;
  event.target.textContent = "Sesli Okuma: " + (voiceEnabled ? "Açık" : "Kapalı");
}

async function sendChat() {
  const input = document.getElementById("chatInput");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  appendMsg("user", text);
  document.getElementById("statusText").textContent = "Düşünüyor ve yanıt üretiyor...";
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text })
  });
  const data = await res.json();
  setEmotion(data.emotion || "happy");
  appendMsg("assistant", data.reply_text || "");
  animateMouth(data.visemes || [], data.reply_text || "");
  document.getElementById("statusText").textContent = "Çevrimiçi ve otonom döngü aktif";
  refreshState();
}

async function triggerCycle() {
  document.getElementById("statusText").textContent = "Otonom döngü çalışıyor...";
  await fetch("/api/cycle", { method: "POST" });
  document.getElementById("statusText").textContent = "Çevrimiçi ve otonom döngü aktif";
  refreshState();
}

async function refreshState() {
  const res = await fetch("/api/state");
  const data = await res.json();
  document.getElementById("brainBox").textContent = JSON.stringify(data.brain_state, null, 2);
  document.getElementById("memoryBox").textContent = JSON.stringify({
    improvements: data.improvements,
    knowledge: data.knowledge
  }, null, 2);
}

refreshState();
setInterval(refreshState, 8000);
</script>
</body>
</html>
"""


class WebAvatarServer:
    def __init__(
        self,
        host: str,
        http_port: int,
        ws_port: int,
        on_chat: Callable[[str], Coroutine[Any, Any, dict[str, Any]]],
        on_cycle: Callable[[], Coroutine[Any, Any, dict[str, Any]]],
        get_state: Callable[[], dict[str, Any]],
    ) -> None:
        self.host = host
        self.http_port = http_port
        self.ws_port = ws_port
        self.on_chat = on_chat
        self.on_cycle = on_cycle
        self.get_state = get_state
        self.runner: web.AppRunner | None = None

    async def _handle_index(self, request: web.Request) -> web.Response:
        return web.Response(text=AVATAR_HTML, content_type="text/html")

    async def _handle_chat(self, request: web.Request) -> web.Response:
        data = await request.json()
        message = str(data.get("message", "")).strip()
        if not message:
            return web.json_response({"error": "message gerekli"}, status=400)
        result = await self.on_chat(message)
        return web.json_response(result)

    async def _handle_cycle(self, request: web.Request) -> web.Response:
        result = await self.on_cycle()
        return web.json_response(result)

    async def _handle_state(self, request: web.Request) -> web.Response:
        return web.json_response(self.get_state())

    async def start(self) -> web.AppRunner:
        app = web.Application()
        app.router.add_get("/", self._handle_index)
        app.router.add_post("/api/chat", self._handle_chat)
        app.router.add_post("/api/cycle", self._handle_cycle)
        app.router.add_get("/api/state", self._handle_state)

        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.host, self.http_port)
        await site.start()
        return self.runner

    async def stop(self) -> None:
        if self.runner:
            await self.runner.cleanup()
