async function send(){

let msg=document.getElementById("msg").value

let res=await fetch("/ai",{

method:"POST",

headers:{"Content-Type":"application/json"},

body:JSON.stringify({message:msg})

})

let data=await res.json()

let chat=document.getElementById("chat")

chat.innerHTML+=`<p>You: ${msg}</p>`

chat.innerHTML+=`<p>AI: ${data.reply}</p>`

}

async function sync(){

await fetch("/sync")

alert("GitHub Synced")

}