$(document).ready(function() {
    let taskCount = 0;

    $('#newTaskBtn').click(function() {
        $('#newTaskForm').removeClass('hidden');
        $('#createXML').addClass('hidden');
        $('#printGraphForm').addClass('hidden');
        $('.graph-execution').addClass('hidden');
        $('#addTimeForm').addClass('hidden');
    });

    $('#createXMLBtn').click(function() {
        $('#createXML').removeClass('hidden');
        $('#newTaskForm').addClass('hidden');
        $('#printGraphForm').addClass('hidden');
        $('.graph-execution').addClass('hidden');
        $('#addTimeForm').addClass('hidden');
    });

    $('#addTaskBtn').click(function() {
        taskCount++;
        const formId = `dynamicTaskForm_${taskCount}`;
        const dynamicFormHtml = `
            <form id="${formId}" class="styled-form">
                <h3>TASK_${taskCount}</h3>
                <div class="form-group">
                    <label for="realTime_${taskCount}">Real Time (true/false)</label>
                    <select id="realTime_${taskCount}" name="realTime_${taskCount}" required>
                        <option value="True">True</option>
                        <option value="False">False</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="taskType_${taskCount}">Task Type (sporadic/periodic)</label>
                    <select id="taskType_${taskCount}" name="taskType_${taskCount}" required>
                        <option value="sporadic">sporadic</option>
                        <option value="periodic">periodic</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="taskId_${taskCount}">Task ID</label>
                    <input type="number" id="taskId_${taskCount}" name="taskId_${taskCount}" min="1" step="1" required>
                </div>

                <div class="form-group">
                    <label for="period_${taskCount}">Period</label>
                    <input type="number" id="period_${taskCount}" name="period_${taskCount}">
                </div>

                <div class="form-group">
                    <label for="activation_${taskCount}">Activation</label>
                    <input type="number" id="activation_${taskCount}" name="activation_${taskCount}" required>
                </div>

                <div class="form-group">
                    <label for="deadline_${taskCount}">Deadline</label>
                    <input type="number" id="deadline_${taskCount}" name="deadline_${taskCount}" required>
                </div>

                <div class="form-group">
                    <label for="wcet_${taskCount}">WCET</label>
                    <input type="number" id="wcet_${taskCount}" name="wcet_${taskCount}" required>
                </div>
            </form>
        `;
        $('#dynamicTaskForm').append(dynamicFormHtml);
    });

    $('#submitAllTasksBtn').click(function() {
        const allTasksData = [];
        const start = parseInt($('#start').val());
        const end = parseInt($('#end').val());
        const schedulingAlgorithm = $('#schedulingAlgorithm').val();
        const quantum = parseInt($('#quantum').val());
        if(isNaN(quantum))
            quantum = 0
        if (isNaN(start) || isNaN(end) || start >= end ) {
            alert('Start time must be less than end time.');
            return;
        }
        if (isNaN(start) || isNaN(end) || start <= -1 ) {
            alert('Start time must be greater than 0.');
            return;
        }
        if (isNaN(start) || isNaN(end) || end <= 0 ) {
            alert('End time must be greater than 0.');
            return;
        }

        if (schedulingAlgorithm === 'RR' && quantum <= 0) {
            alert('Quantum must be greater than 0.');
            return;
        }

        allTasksData.push(start);
        allTasksData.push(end);
        allTasksData.push(schedulingAlgorithm);
        allTasksData.push(quantum);

        for (let i = 1; i <= taskCount; i++) {
            const realtime_id = `#realTime_${i}`;
            const task_type_id = `#taskType_${i}`;
            const taskid_id = `#taskId_${i}`;
            const period_id = `#period_${i}`;
            const activation_id = `#activation_${i}`;
            const deadline_id = `#deadline_${i}`;
            const wcet_id = `#wcet_${i}`;

            // Get field values
            const realTime = $(realtime_id).val();
            const taskType = $(task_type_id).val();
            const taskId = parseInt($(taskid_id).val());
            const period = parseInt($(period_id).val()) || 0;
            const activation = parseInt($(activation_id).val());
            const deadline = parseInt($(deadline_id).val());
            const wcet = parseInt($(wcet_id).val());

            // Validate fields
            if (taskId <= 0) {
                alert('Task ID must be a positive integer for task ' + i);
                return;
            }
            
            if (wcet <= 0) {
                alert('WCET must be a positive integer for task ' + i);
                return;
            }
            if ((taskType === 'periodic' && period <= 0) || (taskType === 'sporadic' && activation < 0)) {
                alert('Invalid period or activation value for task ' + i);
                return;
            }
            if (deadline <= 0) {
                alert('Deadline must be a positive integer for task ' + i);
                return;
            }
            if (taskType === 'periodic' && period >= deadline) {
                alert('Period must be greater than deadline for periodic task ' + i);
                return;
            }
            if (taskType === 'periodic' && wcet > period) {
                alert('WCET must be less than or equal to period for periodic task ' + i);
                return;
            }
            if (deadline < wcet) {
                alert('Deadline must be greater than WCET for task ' + i);
                return;
            }

            allTasksData.push(parseBool(realTime));
            allTasksData.push(taskType);
            allTasksData.push(taskId);
            allTasksData.push(period);
            allTasksData.push(activation);
            allTasksData.push(deadline);
            allTasksData.push(wcet);
        }

        $.ajax({
            url: '/submit_all_tasks',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(allTasksData),
            success: function(response) {
                alert('All tasks submitted successfully!');
                $('#newTaskForm').addClass('hidden');
                $('#createXML').addClass('hidden');
                $('#printGraphForm').addClass('hidden');
                $('.graph-execution').addClass('hidden');
                $('#addTimeForm').addClass('hidden');
            },
            error: function(xhr) {
                const errorMessage = xhr.responseJSON && xhr.responseJSON.error
                    ? xhr.responseJSON.error
                    : 'Error occurred while submitting tasks.';
                console.error(errorMessage);
                alert(errorMessage);
            }
        });
    });

    function parseBool(value) {
        return value.toLowerCase() === 'true';
    }
});
