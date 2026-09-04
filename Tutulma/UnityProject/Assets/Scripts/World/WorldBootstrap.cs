using UnityEngine;

namespace Tutulma.World
{
    public class WorldBootstrap : MonoBehaviour
    {
        private static bool environmentBuilt;

        private void Start()
        {
            if (environmentBuilt)
                return;

            environmentBuilt = true;
            BuildEnvironment();
        }

        private static void BuildEnvironment()
        {
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogDensity = 0.0018f;
            RenderSettings.fogColor = new Color(0.19f, 0.22f, 0.25f);

            Material sky = CreateMaterial("Skybox/Procedural");
            if (sky != null)
            {
                sky.SetFloat("_SunSize", 0.02f);
                sky.SetFloat("_SunSizeConvergence", 5f);
                sky.SetFloat("_AtmosphereThickness", 1.15f);
                sky.SetColor("_SkyTint", new Color(0.32f, 0.39f, 0.48f));
                sky.SetColor("_GroundColor", new Color(0.18f, 0.20f, 0.22f));
                RenderSettings.skybox = sky;
            }

            GameObject ground = new GameObject("ProceduralTerrain");
            TerrainData data = new TerrainData
            {
                heightmapResolution = 257,
                size = new Vector3(1000f, 80f, 1000f)
            };

            float[,] heights = new float[257, 257];
            for (int z = 0; z < 257; z++)
            {
                for (int x = 0; x < 257; x++)
                {
                    float nx = x / 256f;
                    float nz = z / 256f;
                    float large = Mathf.PerlinNoise(nx * 3.1f, nz * 3.1f) * 0.10f;
                    float medium = Mathf.PerlinNoise(nx * 9.5f + 31f, nz * 9.5f + 17f) * 0.035f;
                    float detail = Mathf.PerlinNoise(nx * 28f + 9f, nz * 28f + 44f) * 0.012f;
                    float valley = Mathf.Abs(nx - 0.5f) * 0.035f;
                    heights[z, x] = Mathf.Clamp01(0.035f + large + medium + detail - valley);
                }
            }

            data.SetHeights(0, 0, heights);
            Terrain terrain = ground.AddComponent<Terrain>();
            terrain.terrainData = data;
            terrain.drawInstanced = true;
            TerrainCollider collider = ground.AddComponent<TerrainCollider>();
            collider.terrainData = data;

            GameObject water = GameObject.CreatePrimitive(PrimitiveType.Plane);
            water.name = "Ocean";
            water.transform.position = new Vector3(500f, 4.1f, 500f);
            water.transform.localScale = Vector3.one * 50f;
            water.GetComponent<Renderer>().sharedMaterial = CreateSurfaceMaterial(new Color(0.025f, 0.09f, 0.13f), 0.55f, 0.85f);
            Object.Destroy(water.GetComponent<Collider>());

            CreateLighting();
            CreateVegetation();
            CreateRocks();
        }

        private static void CreateLighting()
        {
            GameObject lightObject = new GameObject("WorldSunLight");
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.2f;
            light.color = new Color(1f, 0.86f, 0.70f);
            light.shadows = LightShadows.Soft;
            light.shadowStrength = 0.85f;
            lightObject.transform.rotation = Quaternion.Euler(32f, -28f, 0f);
        }

        private static void CreateVegetation()
        {
            Material trunk = CreateSurfaceMaterial(new Color(0.16f, 0.09f, 0.045f), 0.8f, 0.1f);
            Material leaves = CreateSurfaceMaterial(new Color(0.07f, 0.19f, 0.08f), 0.7f, 0.05f);

            Random.InitState(1337);
            for (int i = 0; i < 90; i++)
            {
                float x = Random.Range(60f, 940f);
                float z = Random.Range(60f, 940f);
                float y = SampleGround(x, z);
                if (y < 5f)
                    continue;

                GameObject tree = new GameObject("Tree");
                tree.transform.position = new Vector3(x, y, z);

                GameObject trunkObject = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                trunkObject.transform.SetParent(tree.transform);
                trunkObject.transform.localPosition = new Vector3(0f, 3f, 0f);
                trunkObject.transform.localScale = new Vector3(0.45f, 3f, 0.45f);
                trunkObject.GetComponent<Renderer>().sharedMaterial = trunk;
                Object.Destroy(trunkObject.GetComponent<Collider>());

                GameObject crown = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                crown.transform.SetParent(tree.transform);
                crown.transform.localPosition = new Vector3(0f, 7f, 0f);
                crown.transform.localScale = new Vector3(4.5f, 5.5f, 4.5f);
                crown.GetComponent<Renderer>().sharedMaterial = leaves;
                Object.Destroy(crown.GetComponent<Collider>());
            }
        }

        private static void CreateRocks()
        {
            Material rock = CreateSurfaceMaterial(new Color(0.22f, 0.23f, 0.22f), 0.95f, 0.05f);
            Random.InitState(7331);

            for (int i = 0; i < 75; i++)
            {
                float x = Random.Range(20f, 980f);
                float z = Random.Range(20f, 980f);
                float y = SampleGround(x, z);
                if (y < 4.5f)
                    continue;

                GameObject boulder = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                boulder.name = "Rock";
                boulder.transform.position = new Vector3(x, y + Random.Range(0.2f, 1.2f), z);
                float size = Random.Range(1.2f, 4.5f);
                boulder.transform.localScale = new Vector3(size * 1.3f, size, size * 0.85f);
                boulder.transform.rotation = Random.rotation;
                boulder.GetComponent<Renderer>().sharedMaterial = rock;
                Object.Destroy(boulder.GetComponent<Collider>());
            }
        }

        private static float SampleGround(float x, float z)
        {
            float nx = Mathf.Clamp01(x / 1000f);
            float nz = Mathf.Clamp01(z / 1000f);
            float large = Mathf.PerlinNoise(nx * 3.1f, nz * 3.1f) * 0.10f;
            float medium = Mathf.PerlinNoise(nx * 9.5f + 31f, nz * 9.5f + 17f) * 0.035f;
            float detail = Mathf.PerlinNoise(nx * 28f + 9f, nz * 28f + 44f) * 0.012f;
            float valley = Mathf.Abs(nx - 0.5f) * 0.035f;
            return (0.035f + large + medium + detail - valley) * 80f;
        }

        private static Material CreateSurfaceMaterial(Color color, float smoothness, float metallic)
        {
            Material material = CreateMaterial("Universal Render Pipeline/Lit");
            if (material == null)
                material = CreateMaterial("Standard");

            if (material == null)
                return null;

            material.color = color;
            if (material.HasProperty("_Smoothness"))
                material.SetFloat("_Smoothness", smoothness);
            if (material.HasProperty("_Metallic"))
                material.SetFloat("_Metallic", metallic);
            return material;
        }

        private static Material CreateMaterial(string shaderName)
        {
            Shader shader = Shader.Find(shaderName);
            return shader == null ? null : new Material(shader);
        }
    }
}
