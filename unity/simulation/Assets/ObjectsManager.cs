using UnityEngine;

public class ObjectsManager : MonoBehaviour
{
    // Start is called before the first frame update
    public GameObject Bin;
    public GameObject Tape;
    public GameObject Suitcase;
    public GameObject Lamp;
    public GameObject PaperGlobe;
    public int objectCount = 5; // Number of objects to place
    public int gridWidth = 10; // Grid width (same as in GridManager)
    public int gridDepth = 4; // Grid depth (same as in GridManager)
    public float cellSize = 1f; // Cell size (same as in GridManager)
    public int gridHeight = 10; // Height of the grid


    void Start()
    {
        // Access the singleton instance
        SocketClient connection = SocketClient.Instance;
        Debug.Log("[OM]: Object manager started");

        connection.HandleEvent("object_attached", (string[] data) => {
            Debug.Log("[OM]: Callback called started");
            string type = data[1];
            int x = int.Parse(data[2]);
            int y = int.Parse(data[3]);
            int z = int.Parse(data[4]);

            Debug.Log("[OM]:" + type + " " + x + " " + y + " " + z);  

            Vector3 position = new(x * cellSize, (z + 1) * cellSize, y * cellSize);
            GameObject selectedObject = null;
            Quaternion rotation = Quaternion.identity;
            Vector3 translation = new Vector3(0, 0, 0);

            if (type == "bin") {
                selectedObject = Bin;
                rotation = Quaternion.Euler(-90, 0, 0);
                translation = new Vector3(0, -0.5f, 0);
            }

            if (type == "tape") {
                selectedObject = Tape;
                translation = new Vector3(0, -0.43f, 0);
            }

            if (type == "suitcase") {
                selectedObject = Suitcase;
                rotation = Quaternion.Euler(90, 0, 0);
                translation = new Vector3(2f, 0, 2f);
            }

            if (type == "lamp") {
                selectedObject = Lamp;
                translation = new Vector3(0, -0.5f, 0);
            }

            if (type == "paper_globe") {
                selectedObject = PaperGlobe;
                translation = new Vector3(0, -0.42f, 0.9f);
            }

            if (selectedObject != null) {
                Instantiate(selectedObject, position + translation, rotation);
            }
        });
    }


    // Update is called once per frame
    void Update()
    {
        
    }
}
