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
    
        const formData = new FormData(this);

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
            error: function(xhr) {
                const errorMessage = xhr.responseJSON && xhr.responseJSON.error 
                                    ? xhr.responseJSON.error 
                                    : 'Error occurred while creating task.';
                console.error(errorMessage);
                alert(errorMessage);
            }
        });
    });

    $('#createXML').submit(function(event) {
        event.preventDefault();
    
        const formData = new FormData(this);
    
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
            error: function(xhr) {
                const errorMessage = xhr.responseJSON && xhr.responseJSON.error 
                                    ? xhr.responseJSON.error 
                                    : 'Error occurred while creating XML file.';
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
        
        const formData = new FormData(this);

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
            error: function(xhr) {
                const errorMessage = xhr.responseJSON && xhr.responseJSON.error 
                                    ? xhr.responseJSON.error 
                                    : 'Error occurred while uploading XML file.';
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
            error: function(xhr) {
                const errorMessage = xhr.responseJSON && xhr.responseJSON.error 
                                    ? xhr.responseJSON.error 
                                    : 'Error occurred while executing command.';
                console.error('XHR Status:', xhr.status);
                console.error('Error:', xhr.statusText);
                console.error('Response Text:', xhr.responseText);
                alert(errorMessage);
            }
        });
    });

    $('#addTimeBtn').click(function() {
        alert('Add Time button clicked!'); // Alert casuale quando il bottone "add_time" viene premuto
    });

    $('#printGraphBtn').click(function() {
        // Mostra il modulo per i parametri di stampa del grafico
        $('#printGraphForm').removeClass('hidden');
    });

    // Gestisci l'invio del modulo printGraphForm
    $('#printGraphForm').submit(function(event) {
        event.preventDefault();
    
        const formData = {
            start_time: parseInt($('#startTime').val()),
            end_time: parseInt($('#endTime').val()),
            frac_time: parseInt($('#fracTime').val())
        };
    
        $.ajax({
            url: '/print_graph',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                alert(response.message || 'Graph printed successfully!');
                $('#printGraphFormContainer').addClass('hidden');
                location.reload();
            },
            error: function(xhr) {
                const errorMessage = xhr.responseJSON && xhr.responseJSON.error 
                                    ? xhr.responseJSON.error 
                                    : 'Error occurred while printing graph.';
                console.error(errorMessage);
                alert(errorMessage);
            }
        });
    });
});
