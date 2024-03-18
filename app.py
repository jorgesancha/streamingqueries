from flask import Flask, render_template, request, Response, stream_with_context, jsonify, json
from proton_driver import client
import redis
import logging
import re


app = Flask(__name__)


# Setup basic logging
logging.basicConfig(level=logging.DEBUG)

r = redis.Redis()
PUBSUB_CHANNEL = "results"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create-stream', methods=['POST'])
def create_stream():
    data = request.get_json()
    stream_command = data.get('command')

    # Regular expression to match the CREATE STREAM command and capture the stream name
    pattern = r"^CREATE (RANDOM )?STREAM (IF NOT EXISTS )?(?P<db>[a-zA-Z0-9_]+\.)?(?P<name>[a-zA-Z0-9_]+)\s*\("
    match = re.match(pattern, stream_command, re.IGNORECASE)

    if not match:
        return jsonify({"error": "Invalid stream command syntax."}), 400

    stream_name = match.group('name')
    db_prefix = match.group('db') if match.group('db') else ''
    qualified_stream_name = f"{db_prefix}{stream_name}"

    c = client.Client(host='127.0.0.1', port=8463)

    try:
        # Drop the existing stream if it exists
        drop_command = f"DROP STREAM IF EXISTS {qualified_stream_name}"
        c.execute(drop_command)
        logging.info(f"Stream {qualified_stream_name} dropped if it existed.")

        # Execute the original stream creation command
        c.execute(stream_command)
        return jsonify({"success": True, "message": f"Stream {qualified_stream_name} created successfully"}), 200
    except Exception as e:
        # Log the error
        logging.error(f"Failed to create stream: {e}", exc_info=True)

        # Provide a more detailed error message
        error_message = f"An error occurred: {str(e)}" if str(e) else "An unknown error occurred"
        return jsonify({"error": error_message}), 500


@app.route('/run-query', methods=['POST'])
def run_query():
    data = request.get_json()
    query = data.get('query')
    channel = data.get('uuid')

    # Attempt to run the query and stream results
    try:
        c = client.Client(host='127.0.0.1', port=8463)
        rows = c.execute_iter(query)

        for row in rows:
            # Publish each row to the Redis channel that the browser is going to be listening to
            r.publish(channel, json.dumps(row))
            logging.debug(json.dumps(row))

        return jsonify({"message": "Query executed and results published"}), 200
    except Exception as e:
        logging.error(f"Query execution failed: {e}", exc_info=True)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/results/<uuid>')
def results(uuid):
    def event_stream(uuid):
        pubsub = r.pubsub()
        pubsub.subscribe(uuid)  # Subscribe to the channel named with the UUID

        for message in pubsub.listen():
            if message['type'] == 'message':
                yield f"data: {message['data'].decode('utf-8')}\n\n"

    return Response(event_stream(uuid), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True)