const video = document.getElementById("video");

navigator.mediaDevices.getUserMedia({video:true})
.then((stream)=>{
    video.srcObject = stream;
})
.catch((err)=>{
    console.error("Error accessing camera:",err)
    alert("Allow camera permission to use Sentinel AI")
})