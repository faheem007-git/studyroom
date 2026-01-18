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

setInterval(() => {
  fetch(`/room/${ROOM_CODE}/timer`)
    .then(res => res.json())
    .then(data => {
      updateTimerUI(data.remaining, data.state);
    });
}, 1000);

function loadMessages() {
  fetch(`/room/${ROOM_CODE}/messages`)
    .then(res => res.json())
    .then(data => {
      const box = document.getElementById("chat-box");
      box.innerHTML = "";

      data.forEach(m => {
        const div = document.createElement("div");
        div.innerHTML = `<b>${m.user}</b>: ${m.text} <small>${m.time}</small>`;
        box.appendChild(div);
      });

      box.scrollTop = box.scrollHeight;
    });
}

setInterval(loadMessages, 2000);
loadMessages();


document.getElementById("chat-form").addEventListener("submit", e => {
  e.preventDefault();

  const input = document.getElementById("chat-input");

  fetch(`/room/${ROOM_CODE}/send_message`, {
    method: "POST",
    headers: {"Content-Type": "application/x-www-form-urlencoded"},
    body: "message=" + encodeURIComponent(input.value)
  }).then(() => {
    input.value = "";
    loadMessages();
  });
});
