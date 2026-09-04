using UnityEngine;

namespace Tutulma.Player
{
    [RequireComponent(typeof(CharacterController))]
    public class PlayerController : MonoBehaviour
    {
        [SerializeField] private float moveSpeed = 6f;
        [SerializeField] private float sprintSpeed = 10f;
        [SerializeField] private float gravity = -25f;
        [SerializeField] private float jumpHeight = 1.4f;

        private CharacterController controller;
        private Vector3 velocity;

        private void Awake()
        {
            controller = GetComponent<CharacterController>();
        }

        private void Update()
        {
            float x = 0f;
            float z = 0f;

            if (Input.GetKey(KeyCode.A)) x -= 1f;
            if (Input.GetKey(KeyCode.D)) x += 1f;
            if (Input.GetKey(KeyCode.S)) z -= 1f;
            if (Input.GetKey(KeyCode.W)) z += 1f;

            Vector3 input = Vector3.ClampMagnitude(new Vector3(x, 0f, z), 1f);
            float speed = Input.GetKey(KeyCode.LeftShift) ? sprintSpeed : moveSpeed;
            Vector3 movement = transform.TransformDirection(input) * speed;

            if (controller.isGrounded)
            {
                if (velocity.y < 0f)
                    velocity.y = -2f;

                if (Input.GetKeyDown(KeyCode.Space))
                    velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
            }

            velocity.y += gravity * Time.deltaTime;
            controller.Move((movement + velocity) * Time.deltaTime);
        }
    }
}
