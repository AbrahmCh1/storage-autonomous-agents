using System;
using System.Linq;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public delegate void Handler(string[] data);

public class SocketClient : MonoBehaviour
{
    // Singleton instance
    private static SocketClient _instance;

    // Public accessor for the instance
    public static SocketClient Instance
    {
        get
        {
            if (_instance == null)
            {
                // Attempt to find an existing instance
                _instance = FindFirstObjectByType<SocketClient>();

                // If none exists, create a new one
                if (_instance == null)
                {
                    GameObject singletonObject = new GameObject("SocketClient");
                    _instance = singletonObject.AddComponent<SocketClient>();
                    DontDestroyOnLoad(singletonObject);
                }
            }
            return _instance;
        }
    }

    public class Event
    {
        public string type;
        public string data;
    }

    public class EventHandler
    {
        public Handler fx;
        public string eventType;
    }

    private TcpClient client;
    private NetworkStream stream;
    private EventHandler[] handlers;

    private void Awake()
    {
        // Ensure this is the only instance
        if (_instance != null && _instance != this)
        {
            Destroy(gameObject);
            return;
        }

        _instance = this;
        DontDestroyOnLoad(gameObject);
    }

    ~SocketClient() {
        stream.Close();
        client.Close();
    }

    void Start()
    {
        client = new TcpClient("localhost", 65432);
        stream = client.GetStream();

        handlers = Array.Empty<EventHandler>();
    }

    void Update()
    {
        if (stream == null) return;

        byte[] receivedBuffer = new byte[1024];
        if (!stream.DataAvailable) return;

        int bytes = stream.Read(receivedBuffer, 0, receivedBuffer.Length);
        string responseData = Encoding.ASCII.GetString(receivedBuffer, 0, bytes);

        if (string.IsNullOrEmpty(responseData))
            return;

        string[] parts = responseData.Split("\n");
        foreach (string part in parts)
        {
            Event evt = JsonUtility.FromJson<Event>(part);

            foreach (var handler in handlers)
            {
                if (evt.type == handler.eventType)
                {
                    handler.fx?.Invoke(evt.data.Split(",")); // Ensure the delegate is not null
                }
            }
        }
    }

    public void HandleEvent(string evt, Handler fx)
    {
        EventHandler h = new()
        {
            eventType = evt,
            fx = fx
        };

        handlers ??= Array.Empty<EventHandler>();
        handlers = handlers.Append(h).ToArray(); // Create a new array with the new handler
    }
}
