document.addEventListener('DOMContentLoaded', function () {
  const startButton = document.getElementById('start-button');
  const stopButton = document.getElementById('stop-button');
  const videoStream = document.getElementById('video-stream');

  let streamUrl = '';

  startButton.addEventListener('click', async function () {
    streamUrl = '/video_feed_new';
    videoStream.src = streamUrl;
    videoStream.style.display = 'block';
  });

  stopButton.addEventListener('click', async function () {
    if (streamUrl) {
      await fetch('/stop_new');
      videoStream.src = '';
      videoStream.style.display = 'none';
    }
  });
});
