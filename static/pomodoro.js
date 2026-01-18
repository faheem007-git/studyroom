let workTime = 25 * 60;   // 25 minutes
let breakTime = 5 * 60;  // 5 minutes

let timeLeft = workTime;
let isRunning = false;
let isWorkSession = true;
let timerInterval = null;

function updateDisplay() {
  let minutes = Math.floor(timeLeft / 60);
  let seconds = timeLeft % 60;

  document.getElementById("timer").textContent =
    `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

function startTimer() {
  if (isRunning) return;

  isRunning = true;

  timerInterval = setInterval(() => {
    if (timeLeft > 0) {
      timeLeft--;
      updateDisplay();
    } else {
      switchSession();
    }
  }, 1000);
}

function pauseTimer() {
  isRunning = false;
  clearInterval(timerInterval);
}

function resetTimer() {
  pauseTimer();
  isWorkSession = true;
  timeLeft = workTime;
  document.getElementById("session-label").textContent = "Work Session";
  updateDisplay();
}

function switchSession() {
  isWorkSession = !isWorkSession;

  if (isWorkSession) {
    timeLeft = workTime;
    document.getElementById("session-label").textContent = "Work Session";
  } else {
    timeLeft = breakTime;
    document.getElementById("session-label").textContent = "Break Time ☕";
  }
}
