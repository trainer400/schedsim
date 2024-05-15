document.addEventListener('DOMContentLoaded', function() {
    // Gestisci l'invio del form per il caricamento del file XML
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

    // Aggiungi un evento click al bottone di esecuzione
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
