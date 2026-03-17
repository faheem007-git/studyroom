const socket = io();
socket.emit("join", { room_id: ROOM_CODE });
let roomCount = 0;


document.getElementById("createRoomBtn").addEventListener("click", function () {
    roomCount++;

    // Create room card
    const room = document.createElement("div");
    room.classList.add("room-card");
    room.innerHTML = `
        <h3>Room ${roomCount}</h3>
        <button onclick="enterRoom(${roomCount})">Enter Room</button>
    `;

    document.getElementById("roomsContainer").appendChild(room);
});

// Open room page
function enterRoom(id) {
    window.location.href = `room.html?room=${id}`;
}
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const box = document.querySelector(".messages");

form.addEventListener("submit", e => {
  e.preventDefault();

  const msg = input.value.trim();
  if (!msg) return;

  socket.emit("send_message", {
    room_id: ROOM_CODE,
    message: msg
  });

  input.value = "";
});
socket.on("receive_message", data => {
  const div = document.createElement("div");
  div.innerHTML = `<b>${data.username}</b>: ${data.message}`;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
});



const socket = io();

// join room
socket.emit("join", { room_id: ROOM_ID });

// listen for new charts
socket.on("chart_added", (data) => {
    const filesPanel = document.getElementById("filesPanel");

    const div = document.createElement("div");
    div.classList.add("file-item");
    div.innerHTML = `<a href="${data.url}">${data.filename}</a>`;

    filesPanel.appendChild(div);
});
