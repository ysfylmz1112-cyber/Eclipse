using UnityEngine;

namespace Tutulma.Core
{
    public class GameBootstrap : MonoBehaviour
    {
        [SerializeField] private bool buildWorldOnStart = true;

        private void Awake()
        {
            Debug.Log("Tutulma booting...");

            if (buildWorldOnStart)
            {
                TutulmaWorldRuntime.EnsureWorld();
            }
        }
    }

    internal static class TutulmaWorldRuntime
    {
        private static bool built;

        public static void EnsureWorld()
        {
            if (built)
                return;

            built = true;

            if (Object.FindFirstObjectByType<Tutulma.Player.PlayerController>() == null)
            {
                CreatePlayer();
            }

            if (Object.FindFirstObjectByType<Tutulma.World.SunAnomaly>() == null)
            {
                CreateSun();
            }

            if (Object.FindFirstObjectByType<Tutulma.World.WorldBootstrap>() == null)
            {
                CreateWorldController();
            }
        }

        private static void CreatePlayer()
        {
            GameObject player = new GameObject("Player");
            player.transform.position = new Vector3(0f, 2f, 0f);

            CharacterController controller = player.AddComponent<CharacterController>();
            controller.height = 1.8f;
            controller.radius = 0.35f;
            controller.center = new Vector3(0f, 0.9f, 0f);

            player.AddComponent<Tutulma.Player.PlayerController>();

            GameObject cameraObject = new GameObject("PlayerCamera");
            cameraObject.transform.SetParent(player.transform);
            cameraObject.transform.localPosition = new Vector3(0f, 1.55f, 0f);
            cameraObject.transform.localRotation = Quaternion.identity;

            Camera camera = cameraObject.AddComponent<Camera>();
            camera.fieldOfView = 72f;
            camera.nearClipPlane = 0.05f;
            camera.farClipPlane = 2000f;
            cameraObject.AddComponent<Tutulma.Player.PlayerCamera>();

            camera.tag = "MainCamera";
        }

        private static void CreateSun()
        {
            GameObject sun = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            sun.name = "SunAnomaly";
            sun.transform.position = new Vector3(350f, 220f, 500f);
            sun.transform.localScale = Vector3.one * 45f;

            Collider collider = sun.GetComponent<Collider>();
            if (collider != null)
                Object.Destroy(collider);

            MeshRenderer renderer = sun.GetComponent<MeshRenderer>();
            Material material = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            material.color = new Color(1f, 0.25f, 0.03f);
            material.EnableKeyword("_EMISSION");
            material.SetColor("_EmissionColor", new Color(2.5f, 0.08f, 0.01f));
            renderer.sharedMaterial = material;

            Light light = sun.AddComponent<Light>();
            light.type = LightType.Point;
            light.range = 1200f;
            light.intensity = 12f;
            light.color = new Color(1f, 0.45f, 0.2f);
            light.shadows = LightShadows.Soft;

            sun.AddComponent<Tutulma.World.SunAnomaly>();
        }

        private static void CreateWorldController()
        {
            GameObject controller = new GameObject("WorldBootstrap");
            controller.AddComponent<Tutulma.World.WorldBootstrap>();
        }
    }
}
