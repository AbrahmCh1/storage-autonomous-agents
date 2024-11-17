# Simulation server

This server takes care of keeping track of the entire simulation,
deciding where each agent moves, where the objects are, and how full
is each storage.

## Setup

Install the dependencies. We only use python-dotenv to load environment
variables from `.env` file and the OpenAI SDK to make requests

```
pip install python-dotenv openai
```

Setup the environment variables. Use the following command to create a
`.env` file based on `env.example`, and then populate the `OPENAI_API_KEY`
with your valid OpenAI API Key

```
cp .env.example .env
```

Modify possible objects if neccesary by adding or removing images (jpg or png)
to the `server/objects` directory. By default, these are the objects used for
testing. Try to keep the images as small as possible to save in token usage
when vision is performed on them.

```
server/objects
├── baseball.jpg
├── bear.jpg
└── pear.png
```

## Running

To run the server, use the following command

```
python3 server/src/main.py
```

This will open a TCP connection at `127.0.0.1:65432`, and the program will
wait until the Unity simulation connects to this address. Once the connection
is established, the simulation will start and events will be sent to the
Unity simulation as they happen. Simulation will stop when all of the objects
have been collected and stored in Storage objects.
