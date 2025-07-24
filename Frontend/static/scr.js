const id_image = {};

  class ImageDisplayer {
    constructor(zoomContainerId, zoomAreaId) {
      this.zoomContainer = document.getElementById(zoomContainerId);
      this.zoomArea = document.getElementById(zoomAreaId);

      this.scale = 1;
      this.originX = 0;
      this.originY = 0;
      this.startX = 0;
      this.startY = 0;
      this.isDragging = false;

      this.setTransform();

      this.zoomArea.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        this.scale = Math.min(Math.max(0.5, this.scale + delta), 5);
        this.setTransform(); // FIXED: should be this.setTransform()
      });

      this.zoomArea.addEventListener('mousedown', (e) => {
        e.preventDefault();
        this.isDragging = true;
        this.startX = e.clientX - this.originX; // FIXED: was mistakenly assigning to isDragging
        this.startY = e.clientY - this.originY;
      });

      document.addEventListener('mouseup', () => {
        this.isDragging = false;
      });

      document.addEventListener('mousemove', (e) => {
        if (!this.isDragging) return;
        this.originX = e.clientX - this.startX;
        this.originY = e.clientY - this.startY;
        this.setTransform();
      });
    }

    setTransform() {
      this.zoomContainer.style.transform = `translate(${this.originX}px, ${this.originY}px) scale(${this.scale})`;
      this.zoomContainer.style.transformOrigin = '0 0'; // Optional: to ensure scaling is from top-left
    }
  }

// Usage
  // const image = new ImageDisplayer('zoomContainer', 'zoomArea');
  function resetZoom(id) {
      id_image[id].scale = 1;
      id_image[id].originX = 0;
      id_image[id].originY = 0;
      id_image[id].setTransform();
  }

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
        id_image[`${data.id}`] = new ImageDisplayer(`${data.id}1`,`${data.id}2`);
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
});