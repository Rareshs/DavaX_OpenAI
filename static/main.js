const dataScript = document.getElementById("data-script");
const data = dataScript ? JSON.parse(dataScript.textContent) : {};
const recommendedTitles = data.recommendedTitles || [];

let currentAudio = null;
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let stream = null;

const queryInput = document.getElementById("query-input");
const startRecordingBtn = document.getElementById("start-recording-btn");
const playBtn = document.getElementById("play-btn");
const pauseBtn = document.getElementById("pause-btn");
const seekBar = document.getElementById("seek-bar");
const timeLabel = document.getElementById("time-label");
const recordingStatus = document.createElement("div");
recordingStatus.className = "mt-2 text-success small";
recordingStatus.id = "recording-status";
document.querySelector(".input-group").insertAdjacentElement("afterend", recordingStatus);

// Voice recording logic
startRecordingBtn?.addEventListener("click", async () => {
  if (!isRecording) {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];
      isRecording = true;

      mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append("audio", audioBlob, "input.webm");

        recordingStatus.textContent = "🕓 Transcribing...";

        fetch("/voice_transcribe", {
          method: "POST",
          body: formData
        })
          .then(res => res.json())
          .then(data => {
            if (data.transcription) {
              queryInput.value = data.transcription;
              recordingStatus.textContent = "✅ Transcription complete.";
            } else {
              recordingStatus.textContent = "❌ Could not transcribe.";
            }
          });
      };

      mediaRecorder.start();
      recordingStatus.textContent = "🎙️ Listening... Click again to stop.";
      startRecordingBtn.textContent = "🛑 Stop";
    } catch (err) {
      console.error("Mic access error:", err);
      recordingStatus.textContent = "❌ Microphone access denied.";
    }
  } else {
    mediaRecorder.stop();
    stream.getTracks().forEach(track => track.stop());
    isRecording = false;
    startRecordingBtn.textContent = "🎙️ Speak";
    recordingStatus.textContent = "🎙️ Recording stopped.";
  }
});

// Text-to-Speech
playBtn?.addEventListener("click", () => {
  const summary = document.getElementById("ai-result")?.innerText;
  if (!summary) return;

  fetch("/speak", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ summary, model: "tts-1", voice: "nova" })
  })
    .then(res => res.json())
    .then(data => {
      if (data.audio_url) {
        if (currentAudio) {
          currentAudio.pause();
          currentAudio.currentTime = 0;
        }

        currentAudio = new Audio(data.audio_url);

        currentAudio.addEventListener("loadedmetadata", () => {
          seekBar.max = currentAudio.duration;
          timeLabel.textContent = `00:00 / ${formatTime(currentAudio.duration)}`;
        });

        currentAudio.addEventListener("timeupdate", () => {
          seekBar.value = currentAudio.currentTime;
          timeLabel.textContent = `${formatTime(currentAudio.currentTime)} / ${formatTime(currentAudio.duration)}`;
        });

        currentAudio.addEventListener("ended", () => {
          pauseBtn.disabled = true;
          playBtn.disabled = false;
          pauseBtn.textContent = "⏸ Pause";
          seekBar.value = 0;
        });

        currentAudio.play();
        playBtn.disabled = true;
        pauseBtn.disabled = false;
        pauseBtn.textContent = "⏸ Pause";
      } else {
        alert("Error playing voice: " + (data.error || "unknown"));
      }
    });
});
pauseBtn?.addEventListener("click", () => {
  if (currentAudio) {
    if (currentAudio.paused) {
      currentAudio.play();
      pauseBtn.textContent = "⏸ Pause";
    } else {
      currentAudio.pause();
      pauseBtn.textContent = "▶️ Resume";
    }
  }
});

seekBar?.addEventListener("input", () => {
  if (currentAudio) {
    currentAudio.currentTime = seekBar.value;
  }
});

function formatTime(seconds) {
  const m = Math.floor(seconds / 60).toString().padStart(2, "0");
  const s = Math.floor(seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}


// Generate Image buttons
document.getElementById("cover-buttons")?.addEventListener("click", (e) => {
  const btn = e.target.closest(".generate-image");
  if (!btn) return;

  const title = btn.dataset.title?.trim();
  if (!title) return;

  const prompt = `Design a high-quality, visually compelling book cover for the novel titled "${title}". 
Use artwork and typography that reflects the core themes and mood of the story. 
Avoid copyrighted logos. Include the title prominently.`;

  const imageContainer = document.getElementById("image-container");
  imageContainer.innerHTML = `
    <div class="text-center mt-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Generating image for <strong>${title}</strong>...</p>
    </div>
  `;

  fetch("/generate_image", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt })
  })
    .then(res => res.json())
    .then(data => {
      if (data.image_base64) {
        const newCard = document.createElement("div");
        newCard.className = "text-center mb-5";
        newCard.innerHTML = `
          <h5 class="mt-4">Generated Book Cover — ${title}</h5>
          <img src="data:image/png;base64,${data.image_base64}"
               alt="Book cover for ${title}"
               class="img-fluid rounded shadow-sm mt-3"
               style="max-width: 420px;">
        `;
        imageContainer.innerHTML = "";
        imageContainer.appendChild(newCard);
      } else {
        imageContainer.innerHTML = "";
        alert("⚠️ Image generation failed: " + (data.error || "unknown error"));
      }
    })
    .catch((err) => {
      imageContainer.innerHTML = "";
      console.error(err);
      alert("⚠️ Network error while generating image.");
    });
});

// Markdown rendering (move from HTML inline)
document.addEventListener("DOMContentLoaded", () => {
  const el = document.getElementById("ai-result");
  if (el) {
    const md = el.textContent.trim();
    el.innerHTML = marked.parse(md);
  }
});