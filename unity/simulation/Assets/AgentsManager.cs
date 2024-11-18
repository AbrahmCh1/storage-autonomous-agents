using System.Collections;
using System.Collections.Generic;
using System.Linq;
using Unity.VisualScripting;
using UnityEngine;

public class AgentsManager : MonoBehaviour
{
    // Start is called before the first frame update
    public GameObject agentPrefab;
    private Dictionary<string, GameObject> agents = new Dictionary<string, GameObject>();

    class Movement {
        public GameObject agent;
        public Vector3 destination;
        public string type;
    }

    private Movement[] movements = new Movement[0];
    public ObjectsManager objectsManager;


    void Start()
    {
        SocketClient connection = SocketClient.Instance;

        connection.HandleEvent("agent_attached", (string[] data) => {
            string id = data[0];
            int x = int.Parse(data[1]);
            int z = int.Parse(data[2]);
            int y = int.Parse(data[3]);

            GameObject agent = Instantiate(agentPrefab, new Vector3(x, 0.5f, z), Quaternion.identity);
            agents[id] = agent;
        });


        connection.HandleEvent("forward", (string[] data) => {
            string id = data[0];
            GameObject agent = agents[id];
            Animator animator = agent.GetComponent<Animator>();

            animator.SetBool("isRotating", false);
            animator.SetFloat("rotation", 0);

            animator.SetBool("isWalking", true);

            // move the agent forward (where it is facing)
            Vector3 destination = agent.transform.position + agent.transform.forward;

            Movement movement = new() {
                agent = agent,
                destination = destination,
                type = "forward"
            };

            movements = movements.Append(movement).ToArray();
        });

        connection.HandleEvent("rotate", (string[] data) => {
            string id = data[0];
            GameObject agent = agents[id];
            Animator animator = agent.GetComponent<Animator>();
            
            float degrees = float.Parse(data[1]);

            animator.SetBool("isWalking", false);

            animator.SetBool("isRotating", true);
            animator.SetFloat("rotation", degrees > 0 ? 1 : -1);
            
            agent.transform.Rotate(0, degrees, 0);
        });

        connection.HandleEvent("pickup", (string[] data) => {
            string id = data[0];
            GameObject agent = agents[id];
            Animator animator = agent.GetComponent<Animator>();

            GameObject obj = objectsManager.GetObjectById(data[1]);

            obj.transform.parent = agent.transform;
            // have the object be on the head of the agent
            obj.transform.position = new Vector3(0, 0, 0);
            obj.transform.localPosition = new Vector3(0, 0.027f, 0);

            animator.SetBool("isCarrying", true);
        });

        connection.HandleEvent("store", (string[] data) => {
            string id = data[0];
            GameObject agent = agents[id];
            Animator animator = agent.GetComponent<Animator>();

            GameObject obj = objectsManager.GetObjectById(data[1]);

            // hide the object
            obj.SetActive(false);

            animator.SetBool("isCarrying", false);
        });
    }

    void Update() {
        foreach (Movement movement in movements) {
            Animator animator = movement.agent.GetComponent<Animator>();

            if (movement.type == "forward") {
                if (movement.agent.transform.position == movement.destination) {
                    movements = movements.Where(m => m != movement).ToArray();
                    animator.SetBool("isWalking", false);
                } else {
                    movement.agent.transform.position = Vector3.MoveTowards(movement.agent.transform.position, movement.destination, Time.deltaTime * 2f);
                }
            }
        }
    }
}
