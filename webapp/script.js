import { initializeApp } from "https://www.gstatic.com/firebasejs/12.1.0/firebase-app.js";
import { getDatabase, ref, get, set, update, onValue } from "https://www.gstatic.com/firebasejs/12.1.0/firebase-database.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/12.1.0/firebase-analytics.js";

const firebaseConfig = {
  apiKey: "AIzaSyBYrMBCCnb1XiTM8EHn9u-vw7ACHAdvlaQ",
  authDomain: "project-3020568111544941346.firebaseapp.com",
  databaseURL: "https://project-3020568111544941346-default-rtdb.firebaseio.com",
  projectId: "project-3020568111544941346",
  storageBucket: "project-3020568111544941346.firebasestorage.app",
  messagingSenderId: "863166821030",
  appId: "1:863166821030:web:c222bcb42da96f3de1ba67",
  measurementId: "G-ZCNRBT9680"
};

const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const db = getDatabase(app);

let tg = window.Telegram.WebApp;
tg.expand();

let user = {
  id: tg.initDataUnsafe.user?.id || "guest",
  username: tg.initDataUnsafe.user?.username || "guest",
  coins: 0,
  premium: false,
  stats: { games: 0, best_score: 0 }
};

let grid = [];
let score = 0;
let gameOver = false;

function newGame() {
  grid = Array(4).fill().map(() => Array(4).fill(0));
  addTile();
  addTile();
  score = 0;
  gameOver = false;
  render();
}

function addTile() {
  let empty = [];
  for (let i = 0; i < 4; i++)
    for (let j = 0; j < 4; j++)
      if (grid[i][j] === 0) empty.push([i, j]);
  if (empty.length) {
    let [i, j] = empty[Math.floor(Math.random() * empty.length)];
    grid[i][j] = Math.random() < 0.9 ? 2 : 4;
  }
}

function move(dir) {
  if (gameOver) return;
  let moved = false;
  let oldGrid = JSON.stringify(grid);
  let newScore = 0;
  let rotate = (g) => g[0].map((_, i) => g.map(r => r[i]));
  let compress = (row) => {
    let arr = row.filter(x => x);
    while (arr.length < 4) arr.push(0);
    return arr;
  };
  let merge = (row) => {
    for (let i = 0; i < 3; i++)
      if (row[i] && row[i] === row[i + 1]) {
        row[i] *= 2; newScore += row[i]; row[i + 1] = 0;
      }
    return row;
  };

  let handler = (g) => g.map(r => compress(merge(compress(r))));
  if (dir === "left") grid = handler(grid);
  if (dir === "right") grid = handler(grid.map(r => r.reverse())).map(r => r.reverse());
  if (dir === "up") grid = rotate(handler(rotate(grid)));
  if (dir === "down") grid = rotate(handler(rotate(grid.map(r => r.reverse())))).map(r => r.reverse());

  if (JSON.stringify(grid) !== oldGrid) {
    addTile(); score += newScore;
    render();
    checkGameOver();
  }
}

function checkGameOver() {
  for (let i = 0; i < 4; i++)
    for (let j = 0; j < 4; j++)
      if (grid[i][j] === 0)
        return;
  for (let i = 0; i < 4; i++)
    for (let j = 0; j < 4; j++) {
      if (i < 3 && grid[i][j] === grid[i + 1][j]) return;
      if (j < 3 && grid[i][j] === grid[i][j + 1]) return;
    }
  gameOver = true;
  endGame();
}

function endGame() {
  let coinsEarned = Math.floor(score / 100);
  user.coins += coinsEarned;
  user.stats.games += 1;
  if (score > user.stats.best_score) user.stats.best_score = score;
  document.getElementById("coins").textContent = `Coins: ${user.coins}`;
  syncUser();
  updateLeaderboard();
  alert(`Game Over! Score: ${score}. Coins earned: ${coinsEarned}`);
  newGame();
}

function render() {
  let board = document.getElementById("game-board");
  board.innerHTML = "";
  for (let i = 0; i < 4; i++) {
    let row = document.createElement("div");
    row.className = "row";
    for (let j = 0; j < 4; j++) {
      let cell = document.createElement("div");
      cell.className = "cell";
      cell.textContent = grid[i][j] ? grid[i][j] : "";
      row.appendChild(cell);
    }
    board.appendChild(row);
  }
  document.getElementById("coins").textContent = `Coins: ${user.coins}`;
  document.getElementById("premium").textContent = user.premium ? "Premium" : "";
}

async function syncUser() {
  let userRef = ref(db, "users/" + user.id);
  await set(userRef, {
    username: user.username,
    coins: user.coins,
    premium: user.premium,
    stats: user.stats
  });
}

async function updateLeaderboard() {
  let lbRef = ref(db, "leaderboard");
  let snapshot = await get(lbRef);
  let data = snapshot.val() || {};
  let found = false;
  for (let key in data) {
    if (data[key].uid == user.id) {
      found = true;
      await update(ref(db, `leaderboard/${key}`), {
        score: user.stats.best_score,
        coins: user.coins
      });
    }
  }
  if (!found) {
    await set(ref(db, `leaderboard/${Date.now()}_${user.username}`), {
      uid: user.id,
      username: user.username,
      score: user.stats.best_score,
      coins: user.coins
    });
  }
  loadLeaderboard();
}

async function loadLeaderboard() {
  let lbRef = ref(db, "leaderboard");
  let snapshot = await get(lbRef);
  let data = snapshot.val() || {};
  let html = "<h3>Top 10</h3><ul>";
  let sorted = Object.values(data).sort((a, b) => b.score - a.score).slice(0, 10);
  sorted.forEach((u, i) => {
    html += `<li onclick="showUser('${u.username}')">${i + 1}. @${u.username} - ${u.score} (${u.coins || 0} coins)</li>`;
  });
  html += "</ul>";
  document.getElementById("leaderboard").innerHTML = html;
}

window.showUser = async function(username) {
  let usersRef = ref(db, "users");
  let snapshot = await get(usersRef);
  let users = snapshot.val() || {};
  let userObj = Object.values(users).find(u => u.username === username);
  if (userObj) {
    alert(`User: @${userObj.username}\nCoins: ${userObj.coins}\nGames: ${userObj.stats.games}\nBest: ${userObj.stats.best_score}`);
  }
};

async function loadTasks() {
  let tasksRef = ref(db, "tasks");
  let snapshot = await get(tasksRef);
  let tasks = snapshot.val() || {};
  let html = "<h3>Tasks</h3>";
  ["daily", "weekly", "premium"].forEach(section => {
    html += `<h4>${section}</h4><ul>`;
    (tasks[section] || []).forEach((t, i) => {
      html += `<li>${t.name} [${t.reward} coins] (Type: ${t.type}) <button onclick="doTask('${section}',${i},'${t.type}')">Complete</button></li>`;
    });
    html += "</ul>";
  });
  document.getElementById("tasks").innerHTML = html;
}

window.doTask = async function(section, idx, ttype) {
  if (ttype == "subscribe") {
    tg.openTelegramLink('https://t.me/yourchannel');
    document.getElementById("task-action").innerHTML = `<button onclick="confirmSubscribe('${section}',${idx})">I've joined!</button>`;
  } else if (ttype == "code") {
    document.getElementById("task-action").innerHTML = `<input id="secret-code" placeholder="Enter code"><button onclick="confirmCode('${section}',${idx})">Submit</button>`;
  } else {
    completeTask(section, idx);
  }
};

window.confirmSubscribe = async function(section, idx) {
  // Real validation should be server-side via bot
  alert("Channel join verified (demo).");
  completeTask(section, idx);
};

window.confirmCode = async function(section, idx) {
  let code = document.getElementById("secret-code").value;
  if (code !== "SECRET123") {
    alert("Wrong code.");
    return;
  }
  completeTask(section, idx);
};

async function completeTask(section, idx) {
  let tasksRef = ref(db, "tasks");
  let snapshot = await get(tasksRef);
  let tasks = snapshot.val() || {};
  let t = tasks[section][idx];
  user.coins += t.reward;
  await syncUser();
  render();
  alert("Task completed! Coins rewarded.");
}

window.enterPremiumCode = async function() {
  let code = prompt("Enter premium code:");
  if (code === "PREMIUM2048") {
    user.premium = true;
    await syncUser();
    render();
    alert("Premium unlocked!");
  } else {
    alert("Invalid code.");
  }
};

function showAdminPanel() {
  if (user.username === "H08_09") {
    document.getElementById("admin-panel").style.display = "block";
    document.getElementById("admin-panel").innerHTML = `
      <button onclick="addTask()">Add Task</button>
      <button onclick="editTask()">Edit Task</button>
      <button onclick="deleteTask()">Delete Task</button>
      <button onclick="manageUsers()">Manage Users</button>
      <button onclick="viewLeaderboard()">View Leaderboard</button>
    `;
  }
}

window.onload = async function() {
  await syncUser();
  newGame();
  loadLeaderboard();
  loadTasks();
  showAdminPanel();
};