using UnityEngine;

public class GridManager : MonoBehaviour
{
    public int width = 10; // Number of columns in the grid
    public int height = 10; // Number of rows in the grid
    public int depth = 4; // Number of layers in the grid
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
            GenerateGrid();
            GenerateShelves();
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

    void GenerateShelves()
    {
        // Generate shelves for the side at x = 1
        for (int y = 1; y <= 3; y++) // Shelf height
        {
            for (int z = 0; z < depth; z++) // Full range of z
            {
                Vector3 positionSide1 = new Vector3(0 * cellSize, y * cellSize, z * cellSize); // x = 1
                CreateShelf(positionSide1);
            }
        }

        // Generate shelves for the side at x = width (last column)
        for (int y = 1; y <= 3; y++) // Shelf height
        {
            for (int z = 0; z < depth; z++) // Full range of z
            {
                Vector3 positionSide2 = new Vector3((width - 1) * cellSize, y * cellSize, z * cellSize); // x = 10
                CreateShelf(positionSide2);
            }
        }
    }

    void CreateShelf(Vector3 position)
    {
        GameObject shelf = Instantiate(shelfPrefab, position, Quaternion.identity, transform);

        // Assign the shelf material
        Renderer renderer = shelf.GetComponent<Renderer>();
        if (renderer != null)
        {
            renderer.material = shelfMaterial;
        }
    }
}
