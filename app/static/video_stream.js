// videoStream.js
document.addEventListener('DOMContentLoaded', function () {
  const webcamElement = document.getElementById('webcam');
  const processedImageElement = document.getElementById('processedImage');
  const startButton = document.getElementById('startButton');
  const stopButton = document.getElementById('stopButton');

  let webcamStream;
  let isStreaming = false;
  let hasCameraAccess = false;
  const socket = io(SOCKET_URL);
  let intervalId;

  socket.on('processed_frame', (data) => {
    processedImageElement.src = `data:image/jpeg;base64,${data}`;
  });

  socket.on('stop_stream', () => {
    stopStreaming();
  });

  async function startStreaming() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });
      hasCameraAccess = true;
      isStreaming = true;
      webcamStream = stream;
      webcamElement.srcObject = stream;
      webcamElement.play();
      socket.emit('start_stream');
      intervalId = setInterval(captureFrame, 100);
    } catch (error) {
      console.error('Error accessing the camera:', error);
    }
  }

  function stopStreaming() {
    isStreaming = false;
    socket.emit('stop_stream');
    clearInterval(intervalId);
    if (webcamStream) {
      const tracks = webcamStream.getTracks();
      tracks.forEach((track) => track.stop());
    }
    window.location.reload(); // Refresh the page
  }

  function captureFrame() {
    const canvas = document.createElement('canvas');
    canvas.width = webcamElement.videoWidth;
    canvas.height = webcamElement.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(webcamElement, 0, 0, canvas.width, canvas.height);
    const imageSrc = canvas.toDataURL('image/jpeg');
    if (imageSrc) {
      socket.emit('frame', imageSrc);
    }
  }

  startButton.addEventListener('click', startStreaming);
  stopButton.addEventListener('click', stopStreaming);
});
