import express from 'express'
import { body, validationResult } from 'express-validator'
import axios from 'axios'
import { v4 as uuidv4 } from 'uuid'

const router = express.Router()

// AI Service Configuration
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:3002'

// Validation rules
const chatValidation = [
  body('message')
    .isString()
    .trim()
    .isLength({ min: 1, max: 2000 })
    .withMessage('Message must be between 1 and 2000 characters'),
  body('conversationId')
    .optional()
    .isUUID()
    .withMessage('Invalid conversation ID'),
  body('context')
    .optional()
    .isArray()
    .withMessage('Context must be an array')
]

// Chat endpoint
router.post('/', chatValidation, async (req, res) => {
  try {
    // Check validation errors
    const errors = validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      })
    }

    const { message, conversationId, context = [] } = req.body
    const userIP = req.ip || req.connection.remoteAddress

    console.log(`Chat request from ${userIP}:`, { 
      messageLength: message.length,
      hasConversationId: !!conversationId,
      contextLength: context.length
    })

    // Prepare request to AI service
    const aiRequest = {
      message: message.trim(),
      conversationId: conversationId || uuidv4(),
      context: context.slice(-6), // Last 6 messages for context
      userIP,
      timestamp: new Date().toISOString()
    }

    // Call AI service
    const aiResponse = await axios.post(`${AI_SERVICE_URL}/api/chat`, aiRequest, {
      timeout: 30000, // 30 second timeout
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': process.env.AI_SERVICE_API_KEY || 'default-key'
      }
    })

    const { response, conversationId: newConversationId, usage } = aiResponse.data

    // Log usage for analytics
    console.log('AI Service Usage:', {
      conversationId: newConversationId,
      inputTokens: usage?.inputTokens,
      outputTokens: usage?.outputTokens,
      totalTokens: usage?.totalTokens
    })

    res.json({
      response,
      conversationId: newConversationId,
      usage,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Chat route error:', error)

    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNREFUSED') {
        return res.status(503).json({
          error: 'AI service unavailable',
          message: 'The AI service is currently unavailable. Please try again later.'
        })
      }

      if (error.response) {
        return res.status(error.response.status).json({
          error: 'AI service error',
          message: error.response.data?.message || 'Error communicating with AI service'
        })
      }
    }

    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to process chat message'
    })
  }
})

// Get chat history (placeholder - would connect to database)
router.get('/history/:conversationId', async (req, res) => {
  try {
    const { conversationId } = req.params

    // In a real implementation, this would fetch from database
    // For now, return empty array
    res.json({
      conversationId,
      messages: [],
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('History route error:', error)
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to fetch chat history'
    })
  }
})

export default router