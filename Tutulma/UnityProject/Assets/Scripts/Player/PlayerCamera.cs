using UnityEngine;

namespace Tutulma.Player
{
    public class PlayerCamera : MonoBehaviour
    {
        [SerializeField] private float sensitivity = 2.2f;
        [SerializeField] private float minPitch = -85f;
        [SerializeField] private float maxPitch = 85f;

        private Transform player;
        private float pitch;
        private Vector3 lastMousePosition;
        private bool firstFrame = true;

        private void Awake()
        {
            player = transform.parent;
        }

        private void OnEnable()
        {
            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
            lastMousePosition = Input.mousePosition;
            firstFrame = true;
        }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                Cursor.lockState = CursorLockMode.None;
                Cursor.visible = true;
            }

            if (Input.GetMouseButtonDown(0))
            {
                Cursor.lockState = CursorLockMode.Locked;
                Cursor.visible = false;
                lastMousePosition = Input.mousePosition;
                firstFrame = true;
            }

            Vector3 mouse = Input.mousePosition;
            if (firstFrame)
            {
                lastMousePosition = mouse;
                firstFrame = false;
                return;
            }

            if (Cursor.lockState == CursorLockMode.Locked)
            {
                Vector3 delta = mouse - lastMousePosition;
                player.Rotate(Vector3.up, delta.x * sensitivity * 0.05f);
                pitch = Mathf.Clamp(pitch - delta.y * sensitivity * 0.05f, minPitch, maxPitch);
                transform.localRotation = Quaternion.Euler(pitch, 0f, 0f);
            }

            lastMousePosition = mouse;
        }
    }
}
