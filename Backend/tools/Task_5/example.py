    /* Base reset and modern font */
    body {
      margin: 0;
      font-family: "Segoe UI", system-ui, sans-serif;
      background-color: #f0f2f5;
      display: flex;
      flex-direction: column;
      height: 100vh;
    }

    /* Header: File Import */
    .header {
      background: #ffffffdd;
      backdrop-filter: blur(8px);
      border-bottom: 1px solid #ddd;
      padding: 0.75rem 1.25rem;
      display: flex;
      justify-content: flex-end;
    }

    .header button {
      background: #4f46e5;
      color: white;
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 8px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.2s;
    }

    .header button:hover {
      background: #4338ca;
    }

    #file-input {
      display: none;
    }

    /* Chat container */
    .chat-container {
      flex: 1;
      overflow-y: auto;
      padding: 2rem 1rem;
      max-width: 720px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }

    /* Message styling */
    .message {
      padding: 0.85rem 1.25rem;
      max-width: 80%;
      border-radius: 1.1rem;
      font-size: 0.95rem;
      line-height: 1.5;
      white-space: pre-wrap;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    .user {
      background: #e0f7fa;
      color: #004d40;
      align-self: flex-end;
      border-bottom-right-radius: 0.3rem;
    }

    .ai {
      background: #f3f4f6;
      color: #111827;
      align-self: flex-start;
      border-bottom-left-radius: 0.3rem;
    }

    /* Input area */
    .input-wrapper {
      background: white;
      padding: 1rem;
      border-top: 1px solid #ddd;
    }

    .chat-form {
      display: flex;
      align-items: flex-end;
      max-width: 720px;
      margin: 0 auto;
    }

    .chat-form textarea {
      flex: 1;
      padding: 0.75rem 1rem;
      font-size: 1rem;
      border: 1px solid #ccc;
      border-radius: 0.75rem;
      resize: none;
      min-height: 44px;
      max-height: 100px;
      overflow-y: auto;
      box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    }

    .chat-form textarea:focus {
      outline: none;
      border-color: #4f46e5;
      box-shadow: 0 0 0 3px #c7d2fe;
    }

    .chat-form button {
      margin-left: 0.75rem;
      padding: 0.75rem 1.25rem;
      background-color: #4f46e5;
      color: white;
      border: none;
      border-radius: 0.75rem;
      font-size: 1rem;
      cursor: pointer;
      transition: background 0.2s;
    }

    .chat-form button:hover {
      background-color: #4338ca;
    }

    @media (max-width: 600px) {
      .chat-form {
        flex-direction: column;
      }

      .chat-form button {
        width: 100%;
        margin: 0.5rem 0 0;
      }
    }