using UnityEngine;

namespace Tutulma.World
{
    public class SunAnomaly : MonoBehaviour
    {
        [SerializeField] private float growthRate = 0.02f;
        [SerializeField] private float energyPulseSpeed = 1f;
        [SerializeField] private float maxScale = 8f;

        private Vector3 initialScale;
        private float pulseTime;

        private void Start()
        {
            initialScale = transform.localScale;
        }

        private void Update()
        {
            float currentSize = transform.localScale.x;
            float nextSize = Mathf.Min(currentSize + growthRate * Time.deltaTime, initialScale.x * maxScale);
            transform.localScale = Vector3.one * nextSize;

            pulseTime += Time.deltaTime * energyPulseSpeed;
            float pulse = 1f + Mathf.Sin(pulseTime) * 0.04f;
            transform.localScale *= pulse;
        }
    }
}
