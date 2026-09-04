using UnityEngine;

namespace Tutulma.World
{
    public class SunAnomaly : MonoBehaviour
    {
        [SerializeField] private float growthRate = 0.02f;
        [SerializeField] private float energyPulseSpeed = 1f;
        [SerializeField] private float maxScale = 8f;
        [SerializeField] private float pulseAmount = 0.04f;

        private Vector3 initialScale;
        private float pulseTime;
        private float growthScale;

        private void Start()
        {
            initialScale = transform.localScale;
            growthScale = initialScale.x;
        }

        private void Update()
        {
            growthScale = Mathf.Min(
                growthScale + growthRate * Time.deltaTime,
                initialScale.x * maxScale
            );

            pulseTime += Time.deltaTime * energyPulseSpeed;
            float pulse = 1f + Mathf.Sin(pulseTime) * pulseAmount;

            transform.localScale = Vector3.one * growthScale * pulse;
        }
    }
}
