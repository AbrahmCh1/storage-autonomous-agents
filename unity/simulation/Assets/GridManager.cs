using UnityEngine;

public class GridManager : MonoBehaviour
{
    private int width = 10; // Number of columns in the grid
    private int height = 10; // Number of rows in the grid
    private int depth = 4; // Number of layers in the grid
    public float cellSize = 1f; // Size of each cell
    public GameObject cellPrefab; // Prefab for the grid cells
    public GameObject shelfPrefab; // Prefab for the shelves
    public Material solidMaterial; // Material for the bottom layer
    public Material translucentMaterial; // Material for the top layers
    public Material shelfMaterial; // Material for the shelves

    void Start()
    {
        // Access the singleton instance
        SocketClient connection = SocketClient.Instance;

        // Register the event handler
        connection.HandleEvent("warehouse_attached", (string[] data) => {
            int x = int.Parse(data[1]);
            int z = int.Parse(data[2]);
            int y = int.Parse(data[3]);

            height = y + 1;
            width = x;
            depth = z;

            GenerateGrid();
            // GenerateShelves();
        });

        connection.HandleEvent("storage_attached", (string[] data) => {
            int x = int.Parse(data[1]);
            int z = int.Parse(data[2]);
            int y = int.Parse(data[3]);

            Vector3 position = new(x * cellSize, (y + 1) * cellSize, z * cellSize);
            CreateShelf(position);
        });
    }

    void GenerateGrid()
    {
        for (int x = 0; x < width; x++)
        {
            for (int y = 0; y < height; y++)
            {
                for (int z = 0; z < depth; z++)
                {
                    Vector3 position = new Vector3(x * cellSize, y * cellSize, z * cellSize);
                    GameObject cell = Instantiate(cellPrefab, position, Quaternion.identity, transform);

                    // Assign material based on position
                    Renderer renderer = cell.GetComponent<Renderer>();
                    if (renderer != null)
                    {
                        if (y == 0) // Bottom layer
                        {
                            renderer.material = solidMaterial;
                        }
                        else // Top layers
                        {
                            renderer.material = translucentMaterial;
                        }
                    }
                }
            }
        }
    }



    void CreateShelf(Vector3 position)
    {
        Quaternion rotation = Quaternion.Euler(-90, 0, 0);
        GameObject shelf = Instantiate(shelfPrefab, position, rotation, transform);

        // Assign the shelf material
        Renderer renderer = shelf.GetComponent<Renderer>();
        if (renderer != null)
        {
            renderer.material = shelfMaterial;
        }
    }
}
