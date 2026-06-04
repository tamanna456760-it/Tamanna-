import OpenAI from "openai"
import dotenv from "dotenv"

dotenv.config()

const client=new OpenAI({
apiKey:process.env.https://docs.github.com/github-models/quickstart#step-2-make-an-api-call
})

export async function askAI(msg){

const res=await client.chat.completions.create({

model:"gpt-4o-mini",

messages:[
{role:"system",content:"You are Tamanna AI assistant"},
{role:"user",content:msg}
]

})

return res.choices[0].message.content

}