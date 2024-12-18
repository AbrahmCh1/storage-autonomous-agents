using UnityEngine;

public class CameraFollower : MonoBehaviour
{
    public Transform target; // The target object (robot) to follow
    public float heightOffset = 1.0f; // Vertical offset for the camera

    private void LateUpdate()
    {
        if (target != null)
        {
            // Update the camera's position to follow the target with the specified offset
            transform.position = target.position + Vector3.up * heightOffset;
            transform.rotation = target.rotation; // Match the target's rotation
        }
    }
}
