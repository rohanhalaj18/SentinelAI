const express = require("express");
const cors = require("cors");
const http = require("http");
const { Server } = require("socket.io");

const app = express();
app.use(express.json());

app.use(cors());

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
  },
});

//test routes
app.get("/", (req, res) => {
  res.send("Sentinel AI backend is running");
});

io.on("connection", (socket) => {
  console.log("user connected:", socket.id);
  socket.on("disconnect", () => {
    console.log("user disconnected:", socket.id);
  });
});

//alert endpoint
app.post("/alert", (req, res) => {
  const alert = req.body;

  let severity = "LOW";

  if (alert.type === "fight") severity = "HIGH";
  if (alert.type === "knife") severity = "CRITICAL";

  io.emit("newAlert", {
    ...alert,
    severity,
    time: new Date().toLocaleTimeString(),
  });

  res.json({ status: "received" });
});

server.listen(5000, () => {
  console.log("Server started on port 5000");
});
