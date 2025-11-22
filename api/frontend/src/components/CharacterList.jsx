import React from 'react'
import './CharacterList.css'

function CharacterList({ characters, selectedCharacters, onToggleSelection }) {
  return (
    <div className="character-list">
      {characters.map(char => (
        <div
          key={char._id}
          className={`character-card ${selectedCharacters.includes(char._id) ? 'selected' : ''}`}
          onClick={() => onToggleSelection(char._id)}
        >
          <div className="character-info">
            <h3>{char.name}</h3>
            <p className="character-details">
              {char.age}yo {char.race} {char.occupation}
            </p>
            <div className="character-traits">
              {char.personality_traits.slice(0, 3).map((trait, i) => (
                <span key={i} className="trait">{trait}</span>
              ))}
            </div>
          </div>
          {selectedCharacters.includes(char._id) && (
            <div className="selected-badge">✓</div>
          )}
        </div>
      ))}
    </div>
  )
}

export default CharacterList

