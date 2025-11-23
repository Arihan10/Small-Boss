using System;
using UnityEngine;
using UnityEngine.AI;

[RequireComponent(typeof(NavMeshAgent))]
public class CharacterBehaviour : MonoBehaviour
{
    // NavMeshAgent on the same GameObject (required)
    private NavMeshAgent agent;

    // whether the character is currently moving to a destination
    private bool isMoving = false;

    // Optional callback when destination is reached
    public event Action OnReachedDestination;

    // Public read-only accessor
    public bool IsMoving => isMoving;

    void Awake()
    {
        agent = GetComponent<NavMeshAgent>();
    }

    /// <summary>
    /// Move the character to the given world-space position using the NavMeshAgent on this GameObject.
    /// </summary>
    /// <param name="target">World-space destination</param>
    public void MoveTo(Vector3 target)
    {
        if (agent == null)
        {
            agent = GetComponent<NavMeshAgent>();
            if (agent == null)
            {
                Debug.LogError("CharacterBehaviour requires a NavMeshAgent component.");
                return;
            }
        }

        agent.SetDestination(target);
        isMoving = true;
    }

    /// <summary>
    /// Stops the agent immediately.
    /// </summary>
    public void Stop()
    {
        if (agent != null)
        {
            agent.ResetPath();
        }

        isMoving = false;
    }

    void Update()
    {
        // Simple arrival detection: when a path is not pending and remainingDistance <= stoppingDistance
        if (isMoving && agent != null && !agent.pathPending)
        {
            if (agent.remainingDistance <= agent.stoppingDistance)
            {
                // when agent has no path or has effectively stopped moving
                if (!agent.hasPath || agent.velocity.sqrMagnitude == 0f)
                {
                    isMoving = false;
                    OnReachedDestination?.Invoke();
                }
            }
        }
    }
}
