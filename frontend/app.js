const API = "https://ramify.onrender.com";
let selectedFormat = "mp3";
let currentUrl = "";

function setFormat(format) {
  selectedFormat = format;
  document.getElementById("mp3Btn").className =
    `flex-1 py-2 rounded-lg font-semibold ${format === "mp3" ? "bg-red-600" : "bg-gray-700"}`;
  document.getElementById("mp4Btn").className =
    `flex-1 py-2 rounded-lg font-semibold ${format === "mp4" ? "bg-red-600" : "bg-gray-700"}`;
}

async function fetchInfo() {
  const url = document.getElementById("urlInput").value.trim();
  if (!url) return;
  currentUrl = url;
  setStatus("Fetching video info...");

  try {
    const res = await fetch(`${API}/info?url=${encodeURIComponent(url)}`);
    if (!res.ok) throw new Error("Non-OK response");
    const data = await res.json();

    document.getElementById("thumbnail").src = data.thumbnail;
    document.getElementById("title").textContent = data.title;
    document.getElementById("duration").textContent =
      `Duration: ${Math.floor(data.duration / 60)}m ${data.duration % 60}s`;
    document.getElementById("preview").classList.remove("hidden");
    setStatus("");
  } catch {
    setStatus("❌ Failed to fetch video info.");
  }
}

async function downloadFile() {
  if (!currentUrl) return;
  setStatus("⏳ Downloading... this may take a moment.");

  try {
    const res = await fetch(
      `${API}/download?url=${encodeURIComponent(currentUrl)}&format=${selectedFormat}`
    );
    if (!res.ok) throw new Error("Non-OK response");
    const blob = await res.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `download.${selectedFormat}`;
    a.click();
    URL.revokeObjectURL(a.href);
    setStatus("Done!");
  } catch {
    setStatus("Download failed.");
  }
}

function setStatus(msg) {
  document.getElementById("status").textContent = msg;
}
