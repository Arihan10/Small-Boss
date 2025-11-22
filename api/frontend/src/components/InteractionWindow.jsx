import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './InteractionWindow.css'

const API_URL = '/api'

function InteractionWindow({ session, characters, onEnd, onUpdate }) {
  const [advancing, setAdvancing] = useState(false)
  const messagesEndRef = useRef(null)

  const currentTurnChar = characters.find(c => c._id === session.current_turn)
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [session.messages])

  const advanceConversation = async () => {
    setAdvancing(true)
    try {
      const response = await axios.post(
        `${API_URL}/interaction-sessions/${session._id}/advance`
      )
      onUpdate(response.data)
    } catch (error) {
      console.error('Error advancing conversation:', error)
      alert(error.response?.data?.detail || 'Failed to generate response')
    } finally {
      setAdvancing(false)
    }
  }

  const handleEndInteraction = async () => {
    try {
      await axios.post(`${API_URL}/interaction-sessions/${session._id}/end`)
      onEnd()
    } catch (error) {
      console.error('Error ending interaction:', error)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      advanceConversation()
    }
  }

  return (
    <div className="interaction-window">
      <div className="interaction-header">
        <div className="participants">
          <h2>💬 {session.interaction_type}</h2>
          <div className="participant-list">
            {session.participant_names.map((name, i) => (
              <span 
                key={i} 
                className={`participant ${session.participants[i] === session.current_turn ? 'active' : ''}`}
              >
                {name}
                {session.participants[i] === session.current_turn && ' 🗣️'}
              </span>
            ))}
          </div>
        </div>
        <button className="btn-end" onClick={handleEndInteraction}>
          End Interaction
        </button>
      </div>

      <div className="messages-container">
        {session.messages.length === 0 && (
          <div className="no-messages">
            The interaction begins... {currentTurnChar?.name} speaks first.
          </div>
        )}
        {session.messages.map((msg, i) => (
          <div key={i} className={`message ${msg.action}`}>
            <div className="message-author">{msg.character_name}</div>
            <div className="message-content">
              {msg.action === 'talk' ? (
                msg.content
              ) : (
                <em>*{msg.content}*</em>
              )}
            </div>
            <div className="message-time">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <div className="current-turn">
          <strong>🤖 Next: {currentTurnChar?.name}</strong>
          <p className="ai-hint">AI will generate what they say based on personality & context</p>
        </div>
        <div className="input-controls">
          <button 
            onClick={advanceConversation}
            disabled={advancing || !session.is_active}
            className="btn-advance"
            onKeyPress={handleKeyPress}
          >
            {advancing ? '🤖 Generating...' : '▶️ Advance Conversation'}
          </button>
          <p className="tip">Press Enter or click to generate the next response</p>
        </div>
      </div>
    </div>
  )
}

export default InteractionWindow

