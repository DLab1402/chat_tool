document.addEventListener("DOMContentLoaded", () => {
  const id_image = {};

  class ImageDisplayer {
    constructor(frame,img_box,img) {
      console.log(img);
      console.log(img_box);
      this.frame = document.getElementById(frame);
      this.img_box = document.getElementById(img_box);
      this.img = document.getElementById(img);

      // this.first_scale = this.zoomArea.F/768;
      
      this.scale = 1;
      this.originX = 0;
      this.originY = 0;
      this.startX = 0;
      this.startY = 0;
      this.isDragging = false;

      this.setTransform();

      this.img_box.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        this.scale = Math.min(Math.max(0.5, this.scale + delta), 5);
        this.setTransform(); // FIXED: should be this.setTransform()
      });

      this.img_box.addEventListener('mousedown', (e) => {
        e.preventDefault();

        this.isDragging = true;
        
        
        this.startX = e.clientX - this.originX; // FIXED: was mistakenly assigning to isDragging
        this.startY = e.clientY - this.originY;
      });

      this.img_box.addEventListener('mouseup', () => {
        this.isDragging = false;
        this.img.style.cursor = 'grabbing';
      });

      this.img_box.addEventListener('mousemove', (e) => {
        if (!this.isDragging) return;
        this.originX = e.clientX - this.startX;
        this.originY = e.clientY - this.startY;
        // this.img.style.transform = `translate(${this.originX}px, ${this.originY}px) scale(${this.scale})`;
        this.setTransform();
      });

      this.frame.addEventListener('dblclick', () => {
        this.scale = 1;
        this.originX = 0;
        this.originY = 0;
        this.setTransform();
      });

    }

    setTransform() {
      this.img_box.style.transform = `translate(${this.originX}px, ${this.originY}px) scale(${this.scale})`;
      this.img_box.style.transformOrigin = '0 0'; // Optional: to ensure scaling is from top-left
    }
  }

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
      // if (typeof data.ai === "object") {
      //   const message = data.ai.message || JSON.stringify(data.ai);
      //   chatBox.innerHTML += `<div class="message ai">${message}</div>`;
      // } else {
      //   chatBox.innerHTML += `<div class="message ai">${data.ai}</div>`;
      // }
      // if ("id" in data){
      //   id_image[`${data.id}`] = new ImageDisplayer(`${data.id}`,`${data.id}1`,`${data.id}2`);
      //   console.log(id_image);
      // }

      // Luôn luôn append đúng nội dung HTML (không render object/json nữa)
      chatBox.innerHTML += `<div class="message ai">${data.ai}</div>`;

      // Nếu có id (ảnh), gắn event zoom vào ảnh theo id (không render id ra ngoài!)
      if ("id" in data){
        id_image[`${data.id}`] = new ImageDisplayer(`${data.id}`,`${data.id}1`,`${data.id}2`);
        // KHÔNG append id ra chatBox!
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

  document.getElementById("logout").addEventListener("click", async function () {
    await fetch("/logout", {method: "POST"});
    window.location.href = "/login";
  });
});