using UnityEngine;

public class Billboard : MonoBehaviour
{
    public Transform cameraTransform; // Assign your camera here

    void Start()
    {
        // If cameraTransform is not assigned, find the main camera
        if (cameraTransform == null)
        {
            cameraTransform = Camera.main.transform;
        }
    }

    void Update()
    {
        // Make the canvas look at the camera's position
        transform.LookAt(cameraTransform);
    }
}
