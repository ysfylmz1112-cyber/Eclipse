using UnityEngine;

namespace Tutulma.Player
{
    public class PlayerCamera : MonoBehaviour
    {
        [SerializeField] private Transform target;
        [SerializeField] private float distance = 5f;
        [SerializeField] private float height = 2f;
        [SerializeField] private float followSpeed = 10f;

        private void LateUpdate()
        {
            if (target == null)
                return;

            Vector3 desiredPosition = target.position - target.forward * distance + Vector3.up * height;
            transform.position = Vector3.Lerp(transform.position, desiredPosition, followSpeed * Time.deltaTime);
            transform.LookAt(target.position + Vector3.up * 1.2f);
        }
    }
}
