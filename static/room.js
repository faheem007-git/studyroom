document.addEventListener("DOMContentLoaded", function () {

  // -----------------------------
  // SOCKET CONNECTION
  // -----------------------------
  const socket = io();

  if (typeof ROOM_CODE === "undefined") {
    console.error("ROOM_CODE is not defined!");
    return;
  }
  socket. on("connect", () =>{
    console.log("connected:", socket.id);
  
  socket.emit("join", { room_id: ROOM_CODE });

  console.log("Connecting to room:", ROOM_CODE);
  });
  // -----------------------------
  // CHAT SYSTEM
  // -----------------------------
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const messagesBox = document.querySelector(".messages");

  if (form && input && messagesBox) {

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      const message = input.value.trim();
      if (!message) return;

      console.log("Sending message:", message);

      socket.emit("send_message", {
        room_id: ROOM_CODE,
        message: message
      });

      input.value = "";
    });

    socket.on("receive_message", function (data) {
      console.log("Received message:", data);

      const div = document.createElement("div");

      div.innerHTML = `<b>${data.username}</b>: ${data.message}`;

      messagesBox.appendChild(div);

      messagesBox.scrollTop = messagesBox.scrollHeight;
    });
  } else {
    console.warn("Chat elements not found (chat may be disabled)");
  }

  // -----------------------------
  // REAL-TIME FILE SHARING
  // -----------------------------
  const filesPanel = document.getElementById("filesPanel");

  if (filesPanel) {
    socket.on("chart_added", function (data) {
      console.log("New file added:", data);

      const div = document.createElement("div");
      div.classList.add("file-item");

      div.innerHTML = `
        <a href="${data.url}" target="_blank">${data.filename}</a>
      `;

      filesPanel.appendChild(div);
    });
  }

  // -----------------------------
  // FILE PANEL TOGGLE
  // -----------------------------
  const toggleBtn = document.getElementById("toggleFiles");

  if (toggleBtn && filesPanel) {
    toggleBtn.addEventListener("click", function () {
      filesPanel.classList.toggle("active");
    });
  }

  // -----------------------------
  // DEBUG SOCKET EVENTS
  // -----------------------------
  socket.onAny((event, data) => {
    console.log("Socket event:", event, data);
  });




socket.on("update_members",function(members){

  console.log("MEMBER RECEIVED:", members);
  const list = document.querySelector(".member-list");
  

 
  list.innerHTML = "";

  members.forEach(user =>{
    const li = document.createElement("li");
    

    li.innerHTML =`
    <span class="status online"></span>
    <span class="name">● ${user}</span>
    `;
    list.appendChild(li);
  });
});

});