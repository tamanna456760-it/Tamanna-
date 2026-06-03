import OpenAI from "openai"
import dotenv from "dotenv"

dotenv.config()

const client = new OpenAI({
apiKey:process.env.OPENAI_KEY
})

export async function askAI(text){

const res = await client.chat.completions.create({

model:"gpt-4o-mini",

messages:[
{role:"system",content:"You are Tamanna AI assistant"},
{role:"user",content:text}
]

})

return res.choices[0].message.content

}