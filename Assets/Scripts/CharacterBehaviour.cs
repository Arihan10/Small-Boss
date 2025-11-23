using System;
using UnityEngine;
using UnityEngine.AI;

[RequireComponent(typeof(NavMeshAgent))]
public class CharacterBehaviour : MonoBehaviour
{
    // NavMeshAgent on the same GameObject (required)
    private NavMeshAgent agent;

    // whether the character is currently walking to a destination
    private bool isWalking = false;

    // Optional callback when destination is reached
    public event Action OnReachedDestination;

    // Public read-only accessor
    public bool IsWalking => isWalking;

    // Optional Animator on the same GameObject. If present, we will set its "isMoving" bool parameter.
    private Animator animator;

    void Awake()
    {
    agent = GetComponent<NavMeshAgent>();
    animator = GetComponent<Animator>();
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
        isWalking = true;

        // Keep Animator's parameter in sync if an Animator exists. Note: the Animator parameter
        // is expected to be named "isMoving" in the Animator Controller (left as-is for compatibility).
        animator?.SetBool("isMoving", true);
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

        isWalking = false;
        animator?.SetBool("isMoving", false);
    }

    void Update()
    {
        // Simple arrival detection: when a path is not pending and remainingDistance <= stoppingDistance
        if (isWalking && agent != null && !agent.pathPending)
        {
            if (agent.remainingDistance <= agent.stoppingDistance)
            {
                // when agent has no path or has effectively stopped moving
                if (!agent.hasPath || agent.velocity.sqrMagnitude == 0f)
                {
                    isWalking = false;
                    animator?.SetBool("isMoving", false);
                    OnReachedDestination?.Invoke();
                }
            }
        }
    }
}
