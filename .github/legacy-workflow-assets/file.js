const express = require("express");
const bodyParser = require("body-parser");
const app = express();

app.use(bodyParser.json());

let storedData = { text: "" };

app.post("/save", (req, res) => {
  storedData = req.body;
  res.json({ status: "Saved" });
});

app.get("/get", (req, res) => {
  res.json(storedData);
});

app.listen(3000, () => {
  console.log("Server running on port 3000");
});