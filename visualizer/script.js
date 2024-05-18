document.addEventListener('DOMContentLoaded', function() {
    // Aggiungi evento click al bottone "NEW TASK"
    $('#newTaskBtn').click(function() {
        $('#newTaskForm').removeClass('hidden'); // Mostra il form per la nuova task
    });

    // Gestisci l'invio del form per la creazione di una nuova task
$('#newTaskForm').submit(function(event) {
    event.preventDefault(); // Evita il comportamento predefinito del form
    var formData = new FormData(this);
    console.log("FormData:", formData); // Debugging: Mostra i dati del form nella console

    $.ajax({
        url: '/create_task',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            alert('Task created successfully!');
            $('#newTaskForm').addClass('hidden'); // Nascondi il form dopo aver creato la task
        },
        error: function(xhr, status, error) {
            console.error(error);
            alert('Error occurred while creating task.');
        }
    });
});


    // Funzione per gestire l'invio del form per il caricamento del file XML
    $('#xmlForm').submit(function(event) {
        event.preventDefault(); // Evita il comportamento predefinito del form
        var formData = new FormData(this);

        $.ajax({
            url: '/upload_xml',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                alert('XML File uploaded successfully!');
            },
            error: function(xhr, status, error) {
                console.error(error);
                alert('Error occurred while uploading XML file.');
            }
        });
    });

    // Funzione per eseguire la funzione Python
    $('#executeBtn').click(function() {
        $.ajax({
            url: '/execute_function',
            type: 'POST',
            success: function(response) {
                alert(response);
            },
            error: function(xhr, status, error) {
                console.error(error);
                alert('Error occurred while executing function.');
            }
        });
    });
});
