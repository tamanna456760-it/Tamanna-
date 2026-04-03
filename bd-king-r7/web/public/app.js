async function send(){
let msg=document.getElementById("msg").value
let res=await fetch("/ai",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:msg})})
let data=await res.json()
document.getElementById("chat").innerHTML+=`<p>You: ${msg}</p><p>AI: ${data.reply}</p>`
}