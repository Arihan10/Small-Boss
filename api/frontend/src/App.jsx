import React, { useState, useEffect } from 'react'
import axios from 'axios'
import CharacterList from './components/CharacterList'
import InteractionWindow from './components/InteractionWindow'
import ObjectInteraction from './components/ObjectInteraction'
import SpaceActivity from './components/SpaceActivity'
import './App.css'

const API_URL = '/api'

function App() {
  const [characters, setCharacters] = useState([])
  const [selectedCharacters, setSelectedCharacters] = useState([])
  const [activeSession, setActiveSession] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('interactions') // 'interactions', 'objects', or 'spaces'

  useEffect(() => {
    fetchCharacters()
  }, [])

  const fetchCharacters = async () => {
    try {
      const response = await axios.get(`${API_URL}/characters`)
      setCharacters(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching characters:', error)
      setLoading(false)
    }
  }

  const toggleCharacterSelection = (charId) => {
    if (selectedCharacters.includes(charId)) {
      setSelectedCharacters(selectedCharacters.filter(id => id !== charId))
    } else if (selectedCharacters.length < 4) {
      setSelectedCharacters([...selectedCharacters, charId])
    }
  }

  const startInteraction = async () => {
    if (selectedCharacters.length < 2) {
      alert('Select at least 2 characters')
      return
    }

    try {
      const response = await axios.post(`${API_URL}/interaction-sessions/`, {
        character_ids: selectedCharacters,
        interaction_type: 'dialog'
      })
      setActiveSession(response.data)
      setSelectedCharacters([])
    } catch (error) {
      console.error('Error starting interaction:', error)
      alert(error.response?.data?.detail || 'Failed to start interaction')
    }
  }

  const endInteraction = () => {
    setActiveSession(null)
  }

  if (loading) {
    return <div className="app"><div className="loading">Loading characters...</div></div>
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎭 AI Life Simulation - Interaction Tester</h1>
        <p>Medieval Town of Millbrook</p>
        
        {!activeSession && (
          <div className="tab-buttons">
            <button 
              className={`tab-btn ${activeTab === 'interactions' ? 'active' : ''}`}
              onClick={() => setActiveTab('interactions')}
            >
              💬 Conversations
            </button>
            <button 
              className={`tab-btn ${activeTab === 'objects' ? 'active' : ''}`}
              onClick={() => setActiveTab('objects')}
            >
              🎮 Objects
            </button>
            <button 
              className={`tab-btn ${activeTab === 'spaces' ? 'active' : ''}`}
              onClick={() => setActiveTab('spaces')}
            >
              🏰 Spaces
            </button>
          </div>
        )}
      </header>

      <div className="app-content">
        {!activeSession ? (
          <>
            {activeTab === 'interactions' ? (
              <div className="setup-view">
                <div className="selection-panel">
                  <h2>Select Characters to Interact</h2>
                  <p className="instruction">
                    Choose 2-4 characters to start a conversation
                    ({selectedCharacters.length} selected)
                  </p>
                  <CharacterList 
                    characters={characters}
                    selectedCharacters={selectedCharacters}
                    onToggleSelection={toggleCharacterSelection}
                  />
                  <button 
                    className="btn-start"
                    onClick={startInteraction}
                    disabled={selectedCharacters.length < 2}
                  >
                    Start Interaction
                  </button>
                </div>
              </div>
            ) : activeTab === 'objects' ? (
              <ObjectInteraction characters={characters} />
            ) : (
              <SpaceActivity />
            )}
          </>
        ) : (
          <InteractionWindow 
            session={activeSession}
            characters={characters}
            onEnd={endInteraction}
            onUpdate={setActiveSession}
          />
        )}
      </div>
    </div>
  )
}

export default App

