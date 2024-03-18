let evtSource;

document.getElementById('start-stream').addEventListener('click', function() {
    const streamCommand = document.getElementById('stream-command').value;
    fetch('/create-stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command: streamCommand }),
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            document.getElementById('error-message').textContent = data.error || 'An error occurred';
        } else {
            // Handle success case, maybe clear the textarea or show a success message
            document.getElementById('error-message').textContent = data.message;
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        document.getElementById('error-message').textContent = 'An error occurred while sending the request.';
    });
});

document.getElementById('run-query').addEventListener('click', function() {
    const query = document.getElementById('streaming-query').value;
    const uuid = URL.createObjectURL(new Blob()).split('/').pop();

     // Close any existing EventSource
    if (evtSource) {
        evtSource.close();
    }

    fetch('/run-query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query, uuid: uuid }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        console.log("Query sent successfully");
    })
    .catch(error => console.error('Error:', error));
    // Start a new EventSource connection
    let url = "/results/" + uuid
    evtSource = new EventSource(url);

    evtSource.onopen = function(whatever) {
        clearResultsTable();
        console.log(whatever);
        console.log('Event source created: ' + url);
    };        

    evtSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateTableWithNewRow(data); // Assuming you have this function implemented
    };
    
});

function updateTableWithNewRow(data) {
    console.log(data);
    const tableBody = document.getElementById('resultsTable');
    const newRow = tableBody.insertRow();

    data.forEach((value, index) => {
        let cell = newRow.insertCell(index);
        cell.className = "border px-4 py-2";
        cell.textContent = value;
    });

    // Scroll to the latest entry
    const resultsContainer = document.getElementById('resultsTableContainer');
    resultsContainer.scrollTop = resultsContainer.scrollHeight;
}

function clearResultsTable() {
    const tableBody = document.getElementById('resultsTable');
    while (tableBody.firstChild) {
        tableBody.removeChild(tableBody.firstChild);
    }
}