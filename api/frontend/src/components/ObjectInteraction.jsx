import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './ObjectInteraction.css'

const API_URL = '/api'

function ObjectInteraction({ characters }) {
  const [selectedCharacter, setSelectedCharacter] = useState(null)
  const [spaces, setSpaces] = useState([])
  const [selectedSpace, setSelectedSpace] = useState(null)
  const [interacting, setInteracting] = useState(false)
  const [lastInteraction, setLastInteraction] = useState(null)

  useEffect(() => {
    fetchSpaces()
  }, [])

  const fetchSpaces = async () => {
    try {
      const response = await axios.get(`${API_URL}/spaces`)
      setSpaces(response.data)
    } catch (error) {
      console.error('Error fetching spaces:', error)
    }
  }

  const handleUseObject = async (objectName) => {
    if (!selectedCharacter) return

    setInteracting(true)
    try {
      const url = selectedSpace 
        ? `${API_URL}/characters/${selectedCharacter._id}/use/${objectName}?space_id=${selectedSpace._id}`
        : `${API_URL}/characters/${selectedCharacter._id}/use/${objectName}`
      
      const response = await axios.post(url)
      setLastInteraction(response.data)
    } catch (error) {
      console.error('Error using object:', error)
      alert(error.response?.data?.detail || 'Failed to interact with object')
    } finally {
      setInteracting(false)
    }
  }

  return (
    <div className="object-interaction">
      <h2>🎮 Object Interaction Test</h2>
      <p className="subtitle">AI-generated flavor text for character actions</p>

      <div className="interaction-grid">
        {/* Character Selection */}
        <div className="panel">
          <h3>1. Select Character</h3>
          <div className="character-grid">
            {characters.slice(0, 8).map(char => (
              <div
                key={char._id}
                className={`mini-card ${selectedCharacter?._id === char._id ? 'selected' : ''}`}
                onClick={() => setSelectedCharacter(char)}
              >
                <div className="mini-name">{char.name}</div>
                <div className="mini-job">{char.occupation}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Space Selection */}
        <div className="panel">
          <h3>2. Select Space (Optional)</h3>
          <select 
            value={selectedSpace?._id || ''} 
            onChange={(e) => {
              const space = spaces.find(s => s._id === e.target.value)
              setSelectedSpace(space || null)
            }}
            className="space-select"
          >
            <option value="">No specific location</option>
            {spaces.slice(0, 10).map(space => (
              <option key={space._id} value={space._id}>
                {space.name}
              </option>
            ))}
          </select>
        </div>

        {/* Object Selection */}
        <div className="panel">
          <h3>3. Use an Object</h3>
          {selectedSpace ? (
            <div className="object-buttons">
              {selectedSpace.available_objects.slice(0, 8).map((obj, i) => (
                <button
                  key={i}
                  onClick={() => handleUseObject(obj)}
                  disabled={!selectedCharacter || interacting}
                  className="btn-object"
                >
                  {obj.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          ) : (
            <div className="common-objects">
              <p>Common objects:</p>
              <div className="object-buttons">
                {['bench', 'door', 'table', 'chair', 'fountain', 'tree'].map((obj) => (
                  <button
                    key={obj}
                    onClick={() => handleUseObject(obj)}
                    disabled={!selectedCharacter || interacting}
                    className="btn-object"
                  >
                    {obj}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Result Display */}
      {lastInteraction && (
        <div className="result-panel">
          <h3>✨ Generated Flavor Text</h3>
          <div className="flavor-text">
            <div className="interaction-header">
              <strong>{lastInteraction.character_name}</strong> uses{' '}
              <em>{lastInteraction.object_name.replace(/_/g, ' ')}</em>
            </div>
            <div className="interaction-description">
              {lastInteraction.flavor_text}
            </div>
            <div className="interaction-time">
              {new Date(lastInteraction.timestamp).toLocaleTimeString()}
            </div>
          </div>
        </div>
      )}

      {!selectedCharacter && (
        <div className="hint">
          👆 Select a character to begin
        </div>
      )}
    </div>
  )
}

export default ObjectInteraction

