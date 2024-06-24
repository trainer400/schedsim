$(document).ready(function() {
    // Funzione per generare i form dinamici in base al numero di task specificato
    $('#generateTasksBtn').click(function() {
        var taskNumber = document.getElementById('taskNumber').value;
        var container = document.getElementById('dynamicTaskForm');
        container.innerHTML = ''; // Cancella eventuali form esistenti

        for (var i = 1; i <= taskNumber; i++) {
            var form = document.createElement('div');
            form.id = 'taskForm' + i;

            form.innerHTML = `
                <h3>Task ${i}</h3>
                <label for="realTime${i}">Real Time (true/false)</label>
                <select id="realTime${i}" name="realTime${i}" required>
                    <option value="true">true</option>
                    <option value="false">false</option>
                </select>

                <label for="taskType${i}">Task Type (sporadic/periodic)</label>
                <select id="taskType${i}" name="taskType${i}" required>
                    <option value="sporadic">sporadic</option>
                    <option value="periodic">periodic</option>
                </select>

                <label for="taskId${i}">Task ID</label>
                <input type="number" id="taskId${i}" name="taskId${i}" min="1" step="1" required>

                <label for="period${i}">Period</label>
                <input type="number" id="period${i}" name="period${i}">

                <label for="activation${i}">Activation</label>
                <input type="number" id="activation${i}" name="activation${i}" required>

                <label for="deadline${i}">Deadline</label>
                <input type="number" id="deadline${i}" name="deadline${i}" required>

                <label for="wcet${i}">WCET</label>
                <input type="number" id="wcet${i}" name="wcet${i}" required>
            `;

            container.appendChild(form);
        }
    });

    // Funzione per inviare i dati del form XML al server quando viene premuto il tasto
    $('#submitCreateXmlBtn').click(function() {
        // Otteniamo i valori dei campi dal form
        var start = parseInt($('#start').val());
        var end = parseInt($('#end').val());
        var schedulingAlgorithm = $('#schedulingAlgorithm').val();
        var taskNumber = parseInt($('#taskNumber').val());
    
        // Verifichiamo che i valori siano numeri validi
        if (isNaN(start) || isNaN(end) || taskNumber <= 0) {
            alert('Please enter valid values for start, end, and task number.');
            return;
        }
    
        // Creiamo un oggetto per contenere i dati delle task
        var tasks = [];
    
        // Cicliamo attraverso le task e otteniamo i valori dei campi
        for (var i = 1; i <= taskNumber; i++) {
            var realTime = $('#realTime' + i).val();
            var taskType = $('#taskType' + i).val();
            var taskId = parseInt($('#taskId' + i).val());
            var period = parseInt($('#period' + i).val());
            var activation = parseInt($('#activation' + i).val());
            var deadline = parseInt($('#deadline' + i).val());
            var wcet = parseInt($('#wcet' + i).val());
    
            // Verifichiamo che i valori siano numeri validi
            if (isNaN(taskId) || isNaN(period) || isNaN(activation) || isNaN(deadline) || isNaN(wcet)) {
                alert('Please enter valid values for all task fields.');
                return;
            }
    
            // Aggiungiamo i dati della task all'array
            tasks.push({
                realTime: realTime,
                taskType: taskType,
                taskId: taskId,
                period: period,
                activation: activation,
                deadline: deadline,
                wcet: wcet
            });
        }
    
        // Inviamo i dati al server
        $.ajax({
            url: '/create_xml',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                start: start,
                end: end,
                schedulingAlgorithm: schedulingAlgorithm,
                tasks: tasks
            }),
            success: function(response) {
                alert(response.message);
            },
            error: function(xhr, status, error) {
                alert('Error: ' + error);
            }
        });
    });
    
    
    
});
