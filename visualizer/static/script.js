document.addEventListener('DOMContentLoaded', function() {
    let uploadedFilePath = '';

    $('#newTaskBtn').click(function() {
        $('#newTaskForm').removeClass('hidden');
    });

    $('#newTaskForm').submit(function(event) {
        event.preventDefault();
        
        var taskId = $('#taskId').val();
        var period = parseInt($('#period').val());
        var activation = parseInt($('#activation').val());
        var deadline = parseInt($('#deadline').val());
        var wcet = parseInt($('#wcet').val());
        
        // Validazione dei campi
        if (isNaN(period) || isNaN(activation) || isNaN(deadline) || isNaN(wcet) || period <= deadline || wcet <= 0 || deadline <= 0 || taskId <=0) {
            alert('Please fill in all fields correctly.');
            return;
        }

        var formData = new FormData(this);

        $.ajax({
            url: '/create_task',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                alert('Task created successfully!');
                $('#newTaskForm').addClass('hidden');
            },
            error: function(xhr, status, error) {
                console.error(error);
                alert('Error occurred while creating task.');
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
                console.error(error);
                alert('Error occurred while uploading XML file.');
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
                alert(response.output);
            },
            error: function(xhr, status, error) {
                console.error('XHR Status:', status);
                console.error('Error:', error);
                console.error('Response Text:', xhr.responseText);
                alert('Error occurred while executing command.');
            }
        });
    });
});
