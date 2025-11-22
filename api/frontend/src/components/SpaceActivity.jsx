import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './SpaceActivity.css'

const API_URL = '/api'

function SpaceActivity() {
  const [spaces, setSpaces] = useState([])
  const [characters, setCharacters] = useState([])
  const [selectedSpace, setSelectedSpace] = useState(null)
  const [generating, setGenerating] = useState(false)
  const [generatedActivity, setGeneratedActivity] = useState(null)

  useEffect(() => {
    fetchSpaces()
    fetchCharacters()
  }, [])

  const fetchSpaces = async () => {
    try {
      const response = await axios.get(`${API_URL}/spaces`)
      setSpaces(response.data)
    } catch (error) {
      console.error('Error fetching spaces:', error)
    }
  }

  const fetchCharacters = async () => {
    try {
      const response = await axios.get(`${API_URL}/characters`)
      setCharacters(response.data)
    } catch (error) {
      console.error('Error fetching characters:', error)
    }
  }

  const addCharacterToSpace = async (characterId) => {
    if (!selectedSpace) return

    const currentChars = selectedSpace.characters_present || []
    if (currentChars.includes(characterId)) {
      // Remove if already there
      const updated = currentChars.filter(id => id !== characterId)
      await updateSpaceCharacters(updated)
    } else {
      // Add
      await updateSpaceCharacters([...currentChars, characterId])
    }
  }

  const updateSpaceCharacters = async (characterIds) => {
    try {
      const response = await axios.put(
        `${API_URL}/spaces/${selectedSpace._id}/characters`,
        { characters_present: characterIds }
      )
      setSelectedSpace(response.data)
      // Update in spaces list
      setSpaces(spaces.map(s => s._id === response.data._id ? response.data : s))
    } catch (error) {
      console.error('Error updating space:', error)
    }
  }

  const generateActivities = async () => {
    if (!selectedSpace) return

    setGenerating(true)
    try {
      const response = await axios.put(
        `${API_URL}/spaces/${selectedSpace._id}/generate-activities`
      )
      setGeneratedActivity(response.data)
      
      // Refresh the space to get updated description
      const spaceResponse = await axios.get(`${API_URL}/spaces/${selectedSpace._id}`)
      setSelectedSpace(spaceResponse.data)
      setSpaces(spaces.map(s => s._id === spaceResponse.data._id ? spaceResponse.data : s))
    } catch (error) {
      console.error('Error generating activities:', error)
      alert(error.response?.data?.detail || 'Failed to generate activities')
    } finally {
      setGenerating(false)
    }
  }

  const getCharacterName = (charId) => {
    const char = characters.find(c => c._id === charId)
    return char ? char.name : 'Unknown'
  }

  return (
    <div className="space-activity">
      <h2>🏰 Space Activity Generator</h2>
      <p className="subtitle">AI-generated descriptions of what's happening in each location</p>

      <div className="activity-grid">
        {/* Space Selection */}
        <div className="panel">
          <h3>1. Select Space</h3>
          <div className="space-list">
            {spaces.slice(0, 12).map(space => (
              <div
                key={space._id}
                className={`space-card ${selectedSpace?._id === space._id ? 'selected' : ''}`}
                onClick={() => setSelectedSpace(space)}
              >
                <div className="space-name">{space.name}</div>
                <div className="space-count">
                  {space.characters_present?.length || 0} characters
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Character Assignment */}
        {selectedSpace && (
          <div className="panel">
            <h3>2. Add/Remove Characters</h3>
            <div className="character-chips">
              {characters.slice(0, 12).map(char => {
                const isPresent = selectedSpace.characters_present?.includes(char._id)
                return (
                  <div
                    key={char._id}
                    className={`character-chip ${isPresent ? 'present' : ''}`}
                    onClick={() => addCharacterToSpace(char._id)}
                  >
                    {char.name}
                    {isPresent && ' ✓'}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Generate Button */}
        {selectedSpace && (
          <div className="panel">
            <h3>3. Generate Scene</h3>
            <div className="current-scene">
              <p><strong>Current in {selectedSpace.name}:</strong></p>
              {selectedSpace.characters_present?.length > 0 ? (
                <ul className="present-list">
                  {selectedSpace.characters_present.map(charId => (
                    <li key={charId}>{getCharacterName(charId)}</li>
                  ))}
                </ul>
              ) : (
                <p className="empty">No one present</p>
              )}
            </div>
            <button
              onClick={generateActivities}
              disabled={generating}
              className="btn-generate"
            >
              {generating ? '🤖 Generating...' : '✨ Generate Activities'}
            </button>
          </div>
        )}
      </div>

      {/* Result Display */}
      {selectedSpace && (
        <div className="result-panel">
          <h3>📝 {selectedSpace.name}</h3>
          <div className="scene-description">
            {selectedSpace.activities_description || 'No description yet. Generate one!'}
          </div>
        </div>
      )}
    </div>
  )
}

export default SpaceActivity

