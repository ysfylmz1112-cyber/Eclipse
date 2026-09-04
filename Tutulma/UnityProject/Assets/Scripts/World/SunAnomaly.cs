using UnityEngine;

namespace Tutulma.World
{
    public class SunAnomaly : MonoBehaviour
    {
        [SerializeField] private float growthRate = 0.035f;
        [SerializeField] private float energyPulseSpeed = 1.2f;
        [SerializeField] private float maxScale = 8f;
        [SerializeField] private float pulseAmount = 0.045f;

        private Vector3 initialScale;
        private float growthScale;
        private float pulseTime;
        private Light anomalyLight;
        private Material surfaceMaterial;

        private void Start()
        {
            initialScale = transform.localScale;
            growthScale = initialScale.x;
            anomalyLight = GetComponent<Light>();

            Renderer renderer = GetComponent<Renderer>();
            if (renderer != null)
                surfaceMaterial = renderer.sharedMaterial;
        }

        private void Update()
        {
            growthScale = Mathf.Min(
                growthScale + growthRate * Time.deltaTime,
                initialScale.x * maxScale
            );

            pulseTime += Time.deltaTime * energyPulseSpeed;
            float wave = Mathf.Sin(pulseTime);
            float pulse = 1f + wave * pulseAmount;
            transform.localScale = Vector3.one * growthScale * pulse;

            if (anomalyLight != null)
                anomalyLight.intensity = 10f + (wave + 1f) * 4f;

            if (surfaceMaterial != null && surfaceMaterial.HasProperty("_EmissionColor"))
            {
                float emission = 2.0f + (wave + 1f) * 0.7f;
                surfaceMaterial.SetColor("_EmissionColor", new Color(emission, 0.06f, 0.005f));
            }
        }
    }
}
