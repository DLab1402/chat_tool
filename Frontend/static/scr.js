document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const chatBox = document.getElementById("chat-box");
  const textarea = document.getElementById("message-input");

  // Auto-expand textarea
  textarea.addEventListener("input", () => {
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 180) + "px";
  });

  // Submit with Enter key
  textarea.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.requestSubmit(); // Safer than form.submit()
    }
  });

  // Handle form submission via Fetch API
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(chatForm);
    const message = formData.get("message");
    
    chatBox.innerHTML += `<div class="message user">${message}</div>`;

    chatForm.reset();

    const response = await fetch("/chat", {
      method: "POST",
      body: formData
    });

    if (response.ok) {
      const data = await response.json();
      chatBox.innerHTML += `${data.ai}`;
    } else {
      chatBox.innerHTML += `${response.statusText}`;
    }

    textarea.style.height = "auto";
  });

  //Upload files
  document.getElementById("data-input").addEventListener("change", async function () {
    const input = this;
    const files = input.files;
    const formData = new FormData();

    for (const file of files) {
      formData.append("files", file);
    }

      const response = await fetch("/upload", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      const uploaded = result.saved || result.file || [];
      
      if (uploaded.length > 0) {
        const fileListHTML = uploaded.map(f => `<li>${f}</li>`).join("");
        chatBox.innerHTML += `<div>
          Các file được tải lên gồm:
          <ul>${fileListHTML}</ul></div>`;
        
      } else {
        chatBox.innerHTML += `<div class="message ai">Error: ${result.file} hoặc không có file nào thỏa điều kiện.</div>`;
      }
  });
});

const zoomStates = {};

function setupZoomPan(containerId, wrapperId) {
  const container = document.getElementById(containerId);
  const wrapper = document.getElementById(wrapperId);

  if (!container || !wrapper) return;

  let state = {
    scale: 1,
    originX: 0,
    originY: 0,
    isDragging: false,
    startX: 0,
    startY: 0
  };

  zoomStates[containerId] = state;

  container.addEventListener('wheel', (e) => {
    e.preventDefault();
    const delta = e.deltaY < 0 ? 0.1 : -0.1;
    const newScale = Math.min(Math.max(state.scale + delta, 0.1), 5);
    const rect = wrapper.getBoundingClientRect();

    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    state.originX -= (mouseX / state.scale) * delta;
    state.originY -= (mouseY / state.scale) * delta;

    state.scale = newScale;
    updateTransform(containerId, wrapper);
  });

  container.addEventListener('mousedown', (e) => {
    state.isDragging = true;
    state.startX = e.clientX;
    state.startY = e.clientY;
    container.style.cursor = 'grabbing';
  });

  window.addEventListener('mousemove', (e) => {
    if (!state.isDragging) return;
    const dx = (e.clientX - state.startX) / state.scale;
    const dy = (e.clientY - state.startY) / state.scale;
    state.originX += dx;
    state.originY += dy;
    state.startX = e.clientX;
    state.startY = e.clientY;
    updateTransform(containerId, wrapper);
  });

  window.addEventListener('mouseup', () => {
    state.isDragging = false;
    container.style.cursor = 'grab';
  });

  // Initial apply
  updateTransform(containerId, wrapper);
}

function updateTransform(containerId, wrapper) {
  const state = zoomStates[containerId];
  if (!state) return;
  wrapper.style.transform = `translate(${state.originX}px, ${state.originY}px) scale(${state.scale})`;
}

function resetZoom(containerId) {
  const state = zoomStates[containerId];
  const wrapper = document.querySelector(`#${containerId} .image-wrapper`);
  if (!state || !wrapper) return;
  state.scale = 1;
  state.originX = 0;
  state.originY = 0;
  updateTransform(containerId, wrapper);
}