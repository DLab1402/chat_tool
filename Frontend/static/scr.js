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
      if ("id" in data){
        setupZoomPan(`${data.id}`,`${data.id}1`)
      }
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

  const zoomContainer = document.getElementById('zoomContainer');
  const zoomArea = document.getElementById('zoomArea');
  let scale = 1;
  let originX = 0;
  let originY = 0;
  let startX, startY;
  let isDragging = false;

  function setTransform() {
    zoomContainer.style.transform = `translate(${originX}px, ${originY}px) scale(${scale})`;
  }

  function resetZoom() {
    scale = 1;
    originX = 0;
    originY = 0;
    setTransform();
  }

  function openModal() {
    document.getElementById('mapModal').style.display = 'block';
  }

  function closeModal() {
    document.getElementById('mapModal').style.display = 'none';
    resetZoom();
  }

  window.onclick = function(event) {
    const modal = document.getElementById('mapModal');
    if (event.target === modal) {
      closeModal();
    }
  }

  zoomArea.addEventListener('wheel', (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    scale = Math.min(Math.max(0.5, scale + delta), 5);
    setTransform();
  });

  zoomArea.addEventListener('mousedown', (e) => {
    e.preventDefault();
    isDragging = true;
    startX = e.clientX - originX;
    startY = e.clientY - originY;
  });

  document.addEventListener('mouseup', () => {
    isDragging = false;
  });

  document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    originX = e.clientX - startX;
    originY = e.clientY - startY;
    setTransform();
  });

});