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
            <form id="${formId}">
                <label for="realTime_${taskCount}">Real Time (true/false)</label>
                <select id="realTime_${taskCount}" name="realTime_${taskCount}" required>
                    <option value="true">True</option>
                    <option value="false">False</option>
                </select>

                <label for="taskType_${taskCount}">Task Type (sporadic/periodic)</label>
                <select id="taskType_${taskCount}" name="taskType_${taskCount}" required>
                    <option value="sporadic">sporadic</option>
                    <option value="periodic">periodic</option>
                </select>

                <label for="taskId_${taskCount}">Task ID</label>
                <input type="number" id="taskId_${taskCount}" name="taskId_${taskCount}" min="1" step="1" required>

                <label for="period_${taskCount}">Period</label>
                <input type="number" id="period_${taskCount}" name="period_${taskCount}">

                <label for="activation_${taskCount}">Activation</label>
                <input type="number" id="activation_${taskCount}" name="activation_${taskCount}" required>

                <label for="deadline_${taskCount}">Deadline</label>
                <input type="number" id="deadline_${taskCount}" name="deadline_${taskCount}" required>

                <label for="wcet_${taskCount}">WCET</label>
                <input type="number" id="wcet_${taskCount}" name="wcet_${taskCount}" required>
            </form>
        `;
        $('#dynamicTaskForm').append(dynamicFormHtml);
    });

    $('#submitAllTasksBtn').click(function() {
        const allTasksData = [];
        allTasksData.push(parseInt($('#start').val()))
        allTasksData.push(parseInt($('#end').val()))
        allTasksData.push($('#schedulingAlgorithm').val())
        allTasksData.push(parseInt($('#quantum').val()))

        for (let i = 1; i <= taskCount; i++) {
            
            const realtime_id = '#realTime_'+i;
            const task_type_id = 'taskType_'+i;
            const taskid_id = 'taskid_${i}'+i;
            const period_id = "period_${i}"
            const activation_id = 'activation_${i}';
            const deadline_id = "deadline_${i}"
            const wcet_id = 'wcet_${i}';
            allTasksData.push($(realtime_id).val())
            allTasksData.push($(task_type_id).val())
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
});
