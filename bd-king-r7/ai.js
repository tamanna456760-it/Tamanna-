import OpenAI from "openai"

const client = new OpenAI({
apiKey: process.env.OPENAI_KEY
})

export async function startAI(){

console.log("AI Brain Started")

const response = await client.chat.completions.create({

model:"gpt-4o-mini",

messages:[
{role:"system",content:"You are Tamanna AI OS assistant"},
{role:"user",content:"System online"}
]

})

console.log(response.choices[0].message.content)

}