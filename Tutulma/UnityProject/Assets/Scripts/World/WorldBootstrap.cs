using UnityEngine;

namespace Tutulma.World
{
    public class WorldBootstrap : MonoBehaviour
    {
        [SerializeField] private GameObject sun;
        [SerializeField] private GameObject player;

        private void Start()
        {
            if (sun == null)
                Debug.LogWarning("WorldBootstrap: Sun atanmadı.");

            if (player == null)
                Debug.LogWarning("WorldBootstrap: Player atanmadı.");
        }
    }
}
