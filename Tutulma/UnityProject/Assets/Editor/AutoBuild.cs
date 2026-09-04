#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Tutulma.Editor
{
    public static class AutoBuild
    {
        [MenuItem("Tutulma/Build Prototype Scene")]
        public static void Build()
        {
            BuildScene();
        }

        public static void BuildScene()
        {
            EnsureDirectory("Assets/Scenes");

            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            GameObject bootstrap = new GameObject("GameBootstrap");
            bootstrap.AddComponent<Tutulma.Core.GameBootstrap>();

            GameObject camera = new GameObject("PreviewCamera");
            Camera preview = camera.AddComponent<Camera>();
            preview.enabled = false;
            camera.transform.position = new Vector3(0f, 8f, -12f);
            camera.transform.rotation = Quaternion.Euler(20f, 0f, 0f);

            string scenePath = "Assets/Scenes/MainScene.unity";
            EditorSceneManager.SaveScene(SceneManager.GetActiveScene(), scenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log("Tutulma: MainScene generated successfully.");
        }

        private static void EnsureDirectory(string path)
        {
            if (!AssetDatabase.IsValidFolder(path))
            {
                string parent = System.IO.Path.GetDirectoryName(path).Replace('\\', '/');
                string folder = System.IO.Path.GetFileName(path);
                AssetDatabase.CreateFolder(parent, folder);
            }
        }
    }
}
#endif
