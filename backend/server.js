const express = require("express");
const cors = require("cors");
const http = require("http");
const { Server } = require("socket.io")

const app = express();
app.use(cors());

const server = http.createServer(app);
const io=new Server(server,{
    cors:{
        origin:"*",
        methods:["GET","POST"]
    }
})

//test routes
app.get("/",(req,res)=>{
    res.send("Sentinel AI backend is running")
})

io.on("connection", (socket) => {
    console.log("user connected:", socket.id);
    socket.on("disconnect",()=>{
        console.log("user disconnected:", socket.id);
    })
})

server.listen(5000,()=>{
    console.log("Server started on port 5000")
})
