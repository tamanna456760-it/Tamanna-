function ping() {
  const target = document.getElementById("target").value;
  const result = document.getElementById("result");

  result.innerText = "Pinging " + target + " ... ⏳";

  const start = Date.now();

  fetch("https://" + target, { mode: "no-cors" })
    .then(() => {
      const time = Date.now() - start;
      result.innerText =
        "Reply from " + target + " ✅ | Time: " + time + " ms";
    })
    .catch(() => {
      result.innerText =
        "Request timed out ❌ | Host unreachable";
    });
}