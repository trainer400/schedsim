document.addEventListener('DOMContentLoaded', function() {
    let uploadedFilePath = '';

    $('#newTaskBtn').click(function() {
        $('#newTaskForm').removeClass('hidden');
    });

    $('#createXMLBtn').click(function() {
        $('#createXML').removeClass('hidden');
    });

    $('#newTaskForm').submit(function(event) {
        event.preventDefault();
    
        var formData = new FormData(this);

        $.ajax({
            url: '/create_task',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                alert(response.message || 'Task created successfully!');
                $('#newTaskForm').addClass('hidden');
            },
            error: function(xhr, status, error) {
                var errorMessage = xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : 'Error occurred while creating task.';
                console.error(errorMessage);
                alert(errorMessage);
            }
        });
    });

    $('#createXML').submit(function(event) {
        event.preventDefault();
    
        var formData = new FormData(this);
    
        $.ajax({
            url: '/create_xml',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                alert(response.message || 'XML file created successfully!');
                $('#createXML').addClass('hidden');
            },
            error: function(xhr, status, error) {
                var errorMessage = xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : 'Error occurred while creating XML file.';
                console.error(errorMessage);
                alert(errorMessage);
            }
        });
    });
    
    $('#xmlFile').change(function() {
        if (this.files.length > 0) {
            $('#uploadBtn').removeClass('hidden');
        }
    });

    $('#uploadBtn').click(function() {
        $('#xmlForm').submit();
    });

    $('#xmlForm').submit(function(event) {
        event.preventDefault();
        var formData = new FormData(this);

        $.ajax({
            url: '/upload_xml',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                alert('XML File uploaded successfully!');
                uploadedFilePath = response.file_path; // Memorizza il percorso del file caricato
            },
            error: function(xhr, status, error) {
                var errorMessage = xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : 'Error occurred while uploading XML file.';
                console.error(errorMessage);
                alert(errorMessage);
            }
        });
    });

    $('#executeBtn').click(function() {
        if (uploadedFilePath === '') {
            alert('Please upload an XML file first.');
            return;
        }

        $.ajax({
            url: '/execute_main',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ file_path: uploadedFilePath }), // Invia il percorso del file come JSON
            success: function(response) {
                alert(response.output || 'Execution completed successfully!');
            },
            error: function(xhr, status, error) {
                var errorMessage = xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : 'Error occurred while executing command.';
                console.error('XHR Status:', status);
                console.error('Error:', error);
                console.error('Response Text:', xhr.responseText);
                alert(errorMessage);
            }
        });
    });

    $('#addTimeBtn').click(function() {
        alert('Add Time button clicked!'); // Alert casuale quando il bottone "add_time" viene premuto
    });

    $('#printGraphBtn').click(function() {
        // Invia una richiesta POST al server quando il pulsante viene premuto
        $.ajax({
            type: 'POST',
            url: '/print_graph', // Percorso verso la route che gestisce la stampa del grafico
            success: function(response) {
                // Alert di conferma quando la stampa del grafico è avvenuta con successo
                alert(response.message);
                // Aggiorna la pagina dopo aver stampato il grafico
                location.reload();
            },
            error: function(xhr, status, error) {
                // Alert in caso di errore durante la stampa del grafico
                alert('Error: ' + error);
            }
        });
    });
});
