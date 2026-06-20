export default {
async fetch(request) {
return new Response(
JSON.stringify({
status: "online",
service: "Tamanna Worker",
timestamp: new Date().toISOString()
}, null, 2),
{
headers: {
"content-type": "application/json"
}
}
);
}
};