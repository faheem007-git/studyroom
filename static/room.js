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
