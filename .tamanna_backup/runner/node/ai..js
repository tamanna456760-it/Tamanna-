import OpenAI from "openai"
import dotenv from "dotenv"

dotenv.config()

const client = new OpenAI({
apiKey:process.env.OPENAI_KEY
})

export async function askAI(prompt){

const res = await client.chat.completions.create({

model:"gpt-4o-mini",

messages:[
{role:"system",content:"You are a professional software developer"},
{role:"user",content:prompt}
]

})

return res.choices[0].message.content

}