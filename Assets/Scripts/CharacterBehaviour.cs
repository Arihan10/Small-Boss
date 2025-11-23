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

    // whether the character is currently running to a destination
    private bool isRunning = false;

    // Optional callback when destination is reached
    public event Action OnReachedDestination;

    // Public read-only accessors
    public bool IsWalking => isWalking;
    public bool IsRunning => isRunning;

    // Optional Animator on the same GameObject. If present, we will set its "isWalking" and "isRunning" bool parameters.
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
    /// <param name="run">If true, the character runs (speed 5, isRunning=true). Otherwise walks (speed 3, isWalking=true).</param>
    public void MoveTo(Vector3 target, bool run = false)
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

        // Set movement state and speed based on run parameter
        if (run)
        {
            isRunning = true;
            isWalking = false;
            agent.speed = 5f;
            animator?.SetBool("isRunning", true);
            animator?.SetBool("isWalking", false);
        }
        else
        {
            isWalking = true;
            isRunning = false;
            agent.speed = 3f;
            animator?.SetBool("isWalking", true);
            animator?.SetBool("isRunning", false);
        }
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
        isRunning = false;
        animator?.SetBool("isWalking", false);
        animator?.SetBool("isRunning", false);
    }

    void Update()
    {
        // Simple arrival detection: when a path is not pending and remainingDistance <= stoppingDistance
        if ((isWalking || isRunning) && agent != null && !agent.pathPending)
        {
            if (agent.remainingDistance <= agent.stoppingDistance)
            {
                // when agent has no path or has effectively stopped moving
                if (!agent.hasPath || agent.velocity.sqrMagnitude == 0f)
                {
                    isWalking = false;
                    isRunning = false;
                    animator?.SetBool("isWalking", false);
                    animator?.SetBool("isRunning", false);
                    OnReachedDestination?.Invoke();
                }
            }
        }
    }

    /// <summary>
    /// Sets the Interact animation state. Can loop while true.
    /// If true, automatically stops all other action states (Fight, Talk, Kiss, Sex).
    /// </summary>
    /// <param name="isInteracting">True to start/continue interacting, false to stop and return to idle.</param>
    public void Interact(bool isInteracting)
    {
        if (isInteracting)
        {
            animator?.SetBool("isFighting", false);
            animator?.SetBool("isTalking", false);
            animator?.SetBool("isKissing", false);
            animator?.SetBool("isSexing", false);
        }
        animator?.SetBool("isInteracting", isInteracting);
    }

    /// <summary>
    /// Sets the Fight animation state. Can loop while true.
    /// If true, automatically stops all other action states (Interact, Talk, Kiss, Sex).
    /// </summary>
    /// <param name="isFighting">True to start/continue fighting, false to stop and return to idle.</param>
    public void Fight(bool isFighting)
    {
        if (isFighting)
        {
            animator?.SetBool("isInteracting", false);
            animator?.SetBool("isTalking", false);
            animator?.SetBool("isKissing", false);
            animator?.SetBool("isSexing", false);
        }
        animator?.SetBool("isFighting", isFighting);
    }

    /// <summary>
    /// Sets the Talk animation state. Can loop while true.
    /// If true, automatically stops all other action states (Interact, Fight, Kiss, Sex).
    /// </summary>
    /// <param name="isTalking">True to start/continue talking, false to stop and return to idle.</param>
    public void Talk(bool isTalking)
    {
        if (isTalking)
        {
            animator?.SetBool("isInteracting", false);
            animator?.SetBool("isFighting", false);
            animator?.SetBool("isKissing", false);
            animator?.SetBool("isSexing", false);
        }
        animator?.SetBool("isTalking", isTalking);
    }

    /// <summary>
    /// Sets the Kiss animation state. Can loop while true.
    /// If true, automatically stops all other action states (Interact, Fight, Talk, Sex).
    /// </summary>
    /// <param name="isKissing">True to start/continue kissing, false to stop and return to idle.</param>
    public void Kiss(bool isKissing)
    {
        if (isKissing)
        {
            animator?.SetBool("isInteracting", false);
            animator?.SetBool("isFighting", false);
            animator?.SetBool("isTalking", false);
            animator?.SetBool("isSexing", false);
        }
        animator?.SetBool("isKissing", isKissing);
    }

    /// <summary>
    /// Sets the Sex animation state. Can loop while true.
    /// If true, automatically stops all other action states (Interact, Fight, Talk, Kiss).
    /// </summary>
    /// <param name="isSexing">True to start/continue sex animation, false to stop and return to idle.</param>
    public void Sex(bool isSexing)
    {
        if (isSexing)
        {
            animator?.SetBool("isInteracting", false);
            animator?.SetBool("isFighting", false);
            animator?.SetBool("isTalking", false);
            animator?.SetBool("isKissing", false);
        }
        animator?.SetBool("isSexing", isSexing);
    }
}
