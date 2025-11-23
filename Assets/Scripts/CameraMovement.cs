using UnityEngine;
using UnityEngine.InputSystem;

public class CameraMovement : MonoBehaviour
{
    [Header("Movement Settings")]
    public float panSpeed = 0.001f; // Sensitivity for mouse drag

    [Header("Camera Angle")]
    public float pitchAngle = 60f; // Angle looking down (90 is straight down)

    [Header("Height Settings")]
    public float fixedHeight = 40f; // The fixed Y position

    [Header("Position Limits")]
    public Vector2 xLimit = new Vector2(-50f, 50f); // Min X, Max X
    public Vector2 zLimit = new Vector2(-50f, 50f); // Min Z, Max Z

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        // Set the initial rotation
        transform.rotation = Quaternion.Euler(pitchAngle, 0f, 0f);
        
        // Set initial height
        Vector3 startPos = transform.position;
        startPos.y = fixedHeight;
        transform.position = startPos;
    }

    // Update is called once per frame
    void Update()
    {
        // Ensure mouse is connected
        if (Mouse.current == null) return;

        Vector3 pos = transform.position;

        // Mouse Drag Panning (Left Click)
        if (Mouse.current.leftButton.isPressed)
        {
            Vector2 delta = Mouse.current.delta.ReadValue();

            // Move camera opposite to mouse movement to create "drag world" effect
            // We do not multiply by Time.deltaTime because 'delta' is already the pixels moved since the last frame
            pos.x -= delta.x * panSpeed / 300f;
            pos.z -= delta.y * panSpeed / 300f;
            Debug.Log(delta.x * panSpeed);
            Debug.Log(delta.y);
        }

        // Clamp positions
        pos.x = Mathf.Clamp(pos.x, xLimit.x, xLimit.y);
        pos.z = Mathf.Clamp(pos.z, zLimit.x, zLimit.y);
        
        // Enforce fixed height
        pos.y = fixedHeight;

        transform.position = pos;
    }
}
