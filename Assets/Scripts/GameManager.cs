// GameManager.cs
using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Linq;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance;

    Queue<DecisionData> decisionQueue = new Queue<DecisionData>();
    bool isProcessingDecision = false;

    public List<Space> allSpaces = new List<Space>();
    public Dictionary<Character, string> characterLocations = new Dictionary<Character, string>();

    [System.Serializable]
    public class CharacterLocation
    {
        public string character_name;
        public string space_name;
    }

    [System.Serializable]
    public class GlobalContext
    {
        public string time;
        public string[] all_spaces;
        public CharacterLocation[] character_locations;
    }

    public class DecisionData
    {
        public Character character;
        public string triggerSource;

        public DecisionData(Character c, string source)
        {
            character = c;
            triggerSource = source;
        }
    }

    void Awake()
    {
        if (Instance == null)
            Instance = this;
        else
            Destroy(gameObject);

        allSpaces.AddRange(FindObjectsByType<Space>(FindObjectsSortMode.None)); 
    }

    public void UpdateCharacterLocation(Character character, string spaceName)
    {
        if (spaceName == null)
            characterLocations.Remove(character);
        else
            characterLocations[character] = spaceName;
    }

    public GlobalContext GetGlobalContext()
    {
        var locations = characterLocations
            .Select(kvp => new CharacterLocation
            {
                character_name = kvp.Key.name,
                space_name = kvp.Value
            })
            .ToArray();

        return new GlobalContext
        {
            time = "afternoon",
            all_spaces = allSpaces.Select(s => s.spaceName).ToArray(),
            character_locations = locations
        };
    }

    public void QueueDecision(Character character, string triggerSource)
    {
        decisionQueue.Enqueue(new DecisionData(character, triggerSource));

        if (!isProcessingDecision)
            StartCoroutine(ProcessDecisionQueue());
    }

    IEnumerator ProcessDecisionQueue()
    {
        isProcessingDecision = true;

        while (decisionQueue.Count > 0)
        {
            DecisionData decision = decisionQueue.Dequeue();
            yield return StartCoroutine(decision.character.Decide(decision.triggerSource));
        }

        isProcessingDecision = false;
    }
}