let currentMode = null;

function choosePrompt(mode) {
  currentMode = mode;
  const chat = document.getElementById("chat");
  let systemMessage;

  switch (mode) {
    case "modfix":
      systemMessage = "🛠️ ModFix Initializing";
      break;
    case "howto":
      systemMessage = "📘 How-To mode active — ask what you’d like to learn or fix.";
      break;
    case "cheats":
      systemMessage = "🎮 Cheats ready — ask for a category (money, needs, skills, etc.).";
      break;
    case "organize_mods":
      systemMessage = "📂 Mod Organizer active — drop your Mods folder or request cleanup.";
      break;
    case "read_save":
      systemMessage = "💾 Save Reader active — upload or specify the save file to analyze.";
      break;
    default:
      systemMessage = "⚙️ Default mode — describe what you need help with.";
  }

  chat.innerHTML += `<div class="system-message"><i>${systemMessage}</i></div>`;
  chat.scrollTop = chat.scrollHeight;
  highlightActiveButton(mode);
}

async function promptForModsPath() {
  const path = prompt("Could not find your Mods folder automatically.\nPaste or drag it here:");
  if (!path) return;

  const chat = document.getElementById("chat");
  chat.innerHTML += `<div class="system-message"><i>📁 Setting manual Mods folder...</i></div>`;
  chat.scrollTop = chat.scrollHeight;

  try {
    const res = await fetch("/manual_mods_path", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
    const data = await res.json();

    if (data.status === "success" || data.status === "manual_path_received") {
      chat.innerHTML += `<div class="bot-message">✅ Using Mods folder: ${data.path}</div>`;
      chat.innerHTML += `<div class="system-message"><i>🔁 Restarting ModFix with your selected folder...</i></div>`;

      // Close any existing ModFix stream
      if (window.modfixStream) {
        window.modfixStream.close();
      }

      // Start new EventSource for ModFix
      window.modfixStream = new EventSource("/modfix/stream");
      window.modfixStream.onmessage = (event) => {
        chat.innerHTML += `<div class="bot-message">${event.data}</div>`;
        chat.scrollTop = chat.scrollHeight;
      };
      window.modfixStream.onerror = () => {
        chat.innerHTML += `<div class="bot-message error">⚠️ ModFix stream ended or failed.</div>`;
        window.modfixStream.close();
      };
    } else {
      chat.innerHTML += `<div class="bot-message error">❌ ${data.message || "Invalid path response."}</div>`;
    }
  } catch (err) {
    chat.innerHTML += `<div class="bot-message error">⚠️ Error setting path: ${err.message}</div>`;
  }

  chat.scrollTop = chat.scrollHeight;
}

function highlightActiveButton(mode) {
  document.querySelectorAll(".prompt-buttons button").forEach(btn => {
    btn.classList.remove("active");
  });
  const activeButton = document.querySelector(`#btn-${mode}`);
  if (activeButton) activeButton.classList.add("active");
}

async function sendMessage() {
  const msg = document.getElementById("message").value.trim();
  if (!msg) return;

  const chat = document.getElementById("chat");
  chat.innerHTML += `<div class="user-message"><b>You:</b> ${msg}</div>`;
  document.getElementById("message").value = "";
  chat.innerHTML += `<p><i>simsanity is thinking...</i></p>`;
  chat.scrollTop = chat.scrollHeight;

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: msg,
        mode: currentMode,
        timestamp: new Date().toISOString(),
        source: "frontend"
      })
    });

    const data = await res.json();

    chat.innerHTML += `
      <div class="bot-message">
        <b>simsanity (${data.mode || currentMode}):</b> ${data.response || "No response received."}
      </div>
    `;
  } catch (e) {
    console.error("Failed to log user input:", e);
    chat.innerHTML += `<div class="bot-message error">⚠️ Something went wrong. Please try again.</div>`;
  }

  chat.scrollTop = chat.scrollHeight;
}
// Allow pressing Enter to send message
document.getElementById("message").addEventListener("keypress", function(e) {
  if (e.key === "Enter") sendMessage();
});

document.addEventListener("click", async function(event) {
  if (event.target.tagName === "BUTTON") {
    const button = event.target;
    const buttonData = {
      id: button.id || null,
      text: button.innerText,
      timestamp: new Date().toISOString()
    };
    try {
      await fetch('/log_button_click', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buttonData)
      });
    } catch (e) {
      console.error("Failed to log button click:", e);
    }
  }
});

// Handle Cheats button click
document.getElementById("btn-cheats").addEventListener("click", async () => {
  const chat = document.getElementById("chat");
  chat.innerHTML += `<div class="system-message"><b>💡 How to Use Cheats:</b><br>
  1️⃣ Press <b>Ctrl + Shift + C</b> (Windows) or <b>Command + Shift + C</b> (Mac) to open the cheat console.<br>
  2️⃣ Type <b>testingcheats true</b> and press <b>Enter</b> to enable cheats.<br>
  3️⃣ Once enabled, you can type or copy any of the cheats listed below.<br><br>
  🎮 <i>Loading Sims 4 cheats...</i></div>`;
  chat.scrollTop = chat.scrollHeight;

  try {
    const response = await fetch("/cheats", { method: "GET" });
    const data = await response.json();

    if (data.status === "success" && data.cheats) {
      const cheats = data.cheats;
      for (const [category, list] of Object.entries(cheats)) {
        chat.innerHTML += `<div class="bot-message"><b>${category} Cheats:</b></div>`;
        list.forEach(c => {
          chat.innerHTML += `<div class="bot-message"><b>${c['command']}</b><br>${c['description']}</div>`;
        });
      }
    } else {
      chat.innerHTML += `<div class="bot-message error">⚠️ No cheats found or failed to load.</div>`;
    }
  } catch (err) {
    chat.innerHTML += `<div class="bot-message error">⚠️ Error: ${err.message}</div>`;
  }

  // Scroll to top so instructions are visible first
  chat.scrollTop = 0;
});

// Handle How-To button click
document.getElementById("btn-howto").addEventListener("click", async () => {
  const chat = document.getElementById("chat");
  chat.innerHTML += `<div class="system-message"><i>📘 Entering How-To mode...</i></div>`;
  chat.scrollTop = chat.scrollHeight;

  try {
    const response = await fetch("/how_to", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: "howto" })
    });

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const data = await response.json();
    chat.innerHTML += `<div class="bot-message"><b>How-To:</b> ${data.response || "How-To mode ready."}</div>`;
  } catch (err) {
    console.error("How-To fetch error:", err);
    chat.innerHTML += `<div class="bot-message error">⚠️ Error: ${err.message}</div>`;
  }

  chat.scrollTop = chat.scrollHeight;
});

// Handle ModFix button click with chat-based Allow/Deny buttons
document.getElementById("btn-modfix").addEventListener("click", async () => {
  const chat = document.getElementById("chat");
  chat.innerHTML += `<div class="system-message"><i>🧩 Preparing ModFix...</i></div>`;
  chat.scrollTop = chat.scrollHeight;

  try {
    const res = await fetch("/modfix", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ permission_granted: false })
    });

    const data = await res.json();

    if (data.status === "confirm") {
      chat.innerHTML += `
        <div class="bot-message">${data.response}</div>
        <div class="choice-buttons">
          <button id="allow-scan" class="allow">✅ Allow</button>
          <button id="deny-scan" class="deny">❌ Deny</button>
        </div>
      `;
      chat.scrollTop = chat.scrollHeight;

      document.getElementById("allow-scan").addEventListener("click", async () => {
        chat.innerHTML += `<div class="system-message"><i>✅ Permission granted. Searching...</i></div>`;
        const confirmRes = await fetch("/modfix", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ permission_granted: true })
        });
        const confirmData = await confirmRes.json();
        if (confirmData.status === "manual_required") {
          await promptForModsPath();
          return;
        }
        chat.innerHTML += `<div class="bot-message">${confirmData.response}</div>`;

        // After finding folder, start live ModFix progress stream
        const eventSource = new EventSource("/modfix/stream");
        eventSource.onmessage = (event) => {
          chat.innerHTML += `<div class="bot-message">${event.data}</div>`;
          chat.scrollTop = chat.scrollHeight;
        };

        eventSource.onerror = () => {
          chat.innerHTML += `<div class="bot-message error">⚠️ ModFix stream ended or failed.</div>`;
          eventSource.close();
        };

        document.querySelector(".choice-buttons").remove();
      });

      document.getElementById("deny-scan").addEventListener("click", () => {
        chat.innerHTML += `<div class="bot-message error">❌ ModFix scan denied by user. No folders were searched.</div>`;
        document.querySelector(".choice-buttons").remove();
      });

      return;
    } else {
      chat.innerHTML += `<div class="bot-message">${data.response}</div>`;
    }
  } catch (err) {
    chat.innerHTML += `<div class="bot-message error">⚠️ Error: ${err.message}</div>`;
  }

  chat.scrollTop = chat.scrollHeight;
});
