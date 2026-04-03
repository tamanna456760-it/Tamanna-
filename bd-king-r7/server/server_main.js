const express = require("express");
const app = express();
const cors = require("cors");

app.use(cors());
app.use(express.json());
app.use(express.static("public"));

// Include Power Modules
const normal = require("./powerhub/normal");
const medium = require("./powerhub/medium");
const deep = require("./powerhub/deep");
const dark = require("./powerhub/dark");
const underground = require("./powerhub/underground");
const silent = require("./powerhub/silent_supersonic");
const stone = require("./powerhub/stone_spirit");

// API ENDPOINTS
app.get("/power/normal", (req, res) => res.json(normal()));
app.get("/power/medium", (req, res) => res.json(medium()));
app.get("/power/deep", (req, res) => res.json(deep()));
app.get("/power/dark", (req, res) => res.json(dark()));
app.get("/power/underground", (req, res) => res.json(underground()));
app.get("/power/silent", (req, res) => res.json(silent()));
app.get("/power/stone", (req, res) => res.json(stone()));

app.get("/", (req, res) => {
  res.sendFile(__dirname + "/public/index.html");
});

const PORT = 8080;
app.listen(PORT, () => console.log(`PowerHub Running on Port ${PORT}`));
