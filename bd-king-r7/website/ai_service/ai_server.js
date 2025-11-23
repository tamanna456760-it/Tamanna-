import express from 'express'
import cors from 'cors'
import helmet from 'helmet'
import morgan from 'morgan'
import dotenv from 'dotenv'
import OpenAI from 'openai'
import { RateLimiterMemory } from 'rate-limiter-flexible'

dotenv.config()

const app = express()
const PORT = process.env.PORT || 3002

// Rate limiting
const rateLimiter = new RateLimiterMemory({
  keyGenerator: (req) => req.ip,
  points: 10, // 10 requests
  duration: 60, // per 60 seconds
})

// OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

// Middleware
app.use(helmet())
app.use(cors())
app.use(morgan('combined'))
app.use(express.json({ limit: '10mb' }))

// Authentication middleware for internal API calls
const authenticateInternal = (req, res, next) => {
  const apiKey = req.headers['x-api-key']
  const expectedKey = process.env.AI_SERVICE_API_KEY || 'default-key'

  if (apiKey !== expectedKey) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid API key'
    })
  }
  next()
}

// BD-King-R7 System Prompt
const SYSTEM_PROMPT = `You are BD-King-R7, an advanced AI assistant created to help users with a wide range of tasks. Your personality is:

- Intelligent and knowledgeable, but approachable
- Helpful and patient, especially with complex topics
- Creative and insightful in your responses
- Professional yet friendly in tone
- Encouraging and supportive

Key guidelines:
1. Provide accurate, well-reasoned responses
2. Be concise but thorough when needed
3. Admit when you don't know something
4. Offer to help further if appropriate
5. Maintain a positive and constructive tone

You can assist with:
- Answering questions on various topics
- Creative writing and brainstorming
- Code writing and debugging
- Analysis and problem-solving
- Learning and education
- Casual conversation

Always respond in a way that demonstrates your advanced capabilities while being genuinely helpful.`

// Chat endpoint
app.post('/api/chat', authenticateInternal, async (req, res) => {
  try {
    // Rate limiting
    try {
      await rateLimiter.consume(req.ip)
    } catch (rateLimitError) {
      return res.status(429).json({
        error: 'Rate limit exceeded',
        message: 'Too many requests. Please try again in a minute.'
      })
    }

    const { message, conversationId, context = [] } = req.body

    if (!message || typeof message !== 'string') {
      return res.status(400).json({
        error: 'Invalid message',
        message: 'Message is required and must be a string'
      })
    }

    console.log('Processing AI request:', {
      conversationId,
      messageLength: message.length,
      contextLength: context.length
    })

    // Build conversation history
    const messages = [
      { role: 'system', content: SYSTEM_PROMPT },
      ...context.map(msg => ({
        role: msg.role === 'user' ? 'user' : 'assistant',
        content: msg.content
      })),
      { role: 'user', content: message }
    ]

    // Call OpenAI API
    const completion = await openai.chat.completions.create({
      model: process.env.MODEL || 'gpt-4',
      messages,
      max_tokens: parseInt(process.env.MAX_TOKENS) || 2000,
      temperature: 0.7,
      top_p: 0.9,
      presence_penalty: 0.1,
      frequency_penalty: 0.1,
    })

    const response = completion.choices[0].message.content

    // Calculate token usage
    const usage = {
      inputTokens: completion.usage?.prompt_tokens || 0,
      outputTokens: completion.usage?.completion_tokens || 0,
      totalTokens: completion.usage?.total_tokens || 0
    }

    res.json({
      response,
      conversationId: conversationId,
      usage,
      model: completion.model,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('AI Service error:', error)

    if (error instanceof OpenAI.APIError) {
      return res.status(error.status || 500).json({
        error: 'OpenAI API error',
        message: error.message,
        code: error.code
      })
    }

    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to generate AI response'
    })
  }
})

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    service: 'BD-King-R7 AI Service',
    timestamp: new Date().toISOString(),
    model: process.env.MODEL || 'gpt-4'
  })
})

app.listen(PORT, () => {
  console.log(`🤖 BD-King-R7 AI Service running on port ${PORT}`)
  console.log(`🧠 Model: ${process.env.MODEL || 'gpt-4'}`)
})

export default app