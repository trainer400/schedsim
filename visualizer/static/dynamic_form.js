$(document).ready(function () {
    let taskCount = 0;

    $('#newTaskBtn').click(function () {
        $('#newTaskForm').removeClass('hidden');
        $('#createXML').addClass('hidden');
        $('#printGraphForm').addClass('hidden');
        $('.graph-execution').addClass('hidden');
        $('#addTimeForm').addClass('hidden');
    });

    function toggleFields(taskCount) {
        var taskType = $(`#taskType_${taskCount}`).val();
        var periodGroup = $(`#periodGroup_${taskCount}`);
        var activationGroup = $(`#activationGroup_${taskCount}`);

        if (taskType === "periodic") {
            periodGroup.removeClass("hidden");
            activationGroup.addClass("hidden");
        } else if (taskType === "sporadic") {
            periodGroup.addClass("hidden");
            activationGroup.removeClass("hidden");
        } else {
            periodGroup.addClass("hidden");
            activationGroup.addClass("hidden");
        }

        console.log("Period Group hidden:", periodGroup.hasClass('hidden'));
        console.log("Activation Group hidden:", activationGroup.hasClass('hidden'));
    }

    $('#createXMLBtn').click(function () {
        $('#createXML').removeClass('hidden');
        $('#newTaskForm').addClass('hidden');
        $('#printGraphForm').addClass('hidden');
        $('.graph-execution').addClass('hidden');
        $('#addTimeForm').addClass('hidden');
    });

    $('#addTaskBtn').click(function () {
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

                <div class=" hidden" id="periodGroup_${taskCount}">
                    <div class="form-group" >
                        <label for="period_${taskCount}">Period</label>
                        <input type="number" id="period_${taskCount}" name="period_${taskCount}">
                    </div>
                    
                </div>
                

                <div class=" hidden" id="activationGroup_${taskCount}">
                    <div class="form-group ">
                        <label for="activation_${taskCount}">Activation</label>
                        <input type="number" id="activation_${taskCount}" name="activation_${taskCount}">
                    </div> 
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

        $(`#taskType_${taskCount}`).change(function () {
            toggleFields(taskCount);
        });

        toggleFields(taskCount);
    });

    $('#submitAllTasksBtn').click(function () {
        jsonObject = {
            startTime: 0,
            endTime: 0,
            schedulingAlgorithm: "",
            serverAlgorithm: "",
            quantum: 0,
            serverCapacity: 0,
            serverPeriod: 0,
            tasks: []
        };

        const start = parseInt($('#start').val());
        const end = parseInt($('#end').val());
        const schedulingAlgorithm = $('#schedulingAlgorithm').val();
        let serverAlgorithm = $('#serverAlgorithm').val();
        let serverCapacity = $('#serverCapacity').val();
        let serverPeriod = $('#serverPeriod').val();
        let quantum = parseInt($('#quantum').val());
        if (isNaN(quantum)) { quantum = 0; }
        if (isNaN(serverCapacity)) { serverCapacity = 0; }
        if (isNaN(serverPeriod)) { serverPeriod = 0; }
        if (isNaN(start) || isNaN(end) || start >= end || start < 0 || end <= 0) {
            alert('Start time must be less than end time and greater than 0.');
            return;
        }
        if (schedulingAlgorithm === 'RR' && quantum <= 0) {
            alert('Quantum must be greater than 0.');
            return;
        }
        if (schedulingAlgorithm === 'RM' && (serverCapacity <= 0 || serverPeriod <= 0)) {
            alert('Server capacity and server period must be greater than 0');
            return;
        }

        jsonObject.startTime = start;
        jsonObject.endTime = end;
        jsonObject.schedulingAlgorithm = schedulingAlgorithm;
        jsonObject.serverAlgorithm = serverAlgorithm;
        jsonObject.quantum = quantum;
        jsonObject.serverCapacity = serverCapacity;
        jsonObject.serverPeriod = serverPeriod;

        for (let i = 1; i <= taskCount; i++) {
            taskObject = {
                real_time: false,
                type: "",
                id: 0,
                period: 0,
                activation: 0,
                deadline: 0,
                wcet: 0
            };

            const realTime = $(`#realTime_${i}`).val();
            const taskType = $(`#taskType_${i}`).val();
            const taskId = parseInt($(`#taskId_${i}`).val());
            const period = parseInt($(`#period_${i}`).val()) || 0;
            const activation = parseInt($(`#activation_${i}`).val()) || 0;
            const deadline = parseInt($(`#deadline_${i}`).val());
            const wcet = parseInt($(`#wcet_${i}`).val());

            if (taskId <= 0 || wcet <= 0 || deadline <= 0) {
                alert(`Invalid inputs for task ${i}.`);
                return;
            }

            if ((taskType === 'periodic' && (period <= 0 || period >= deadline || wcet > period)) ||
                (taskType === 'sporadic' && activation < 0) ||
                (deadline < wcet)) {
                alert(`Invalid scheduling parameters for task ${i}.`);
                return;
            }

            taskObject.real_time = parseBool(realTime);
            taskObject.type = taskType;
            taskObject.id = taskId;
            taskObject.period = period;
            taskObject.activation = activation;
            taskObject.deadline = deadline;
            taskObject.wcet = wcet;

            jsonObject.tasks.push(taskObject);
        }

        console.log(JSON.stringify(jsonObject))

        $.ajax({
            url: '/submit_all_tasks',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(jsonObject),
            success: function (response) {
                alert('All tasks submitted successfully!');
                $('#newTaskForm').addClass('hidden');
                $('#createXML').addClass('hidden');
                $('#printGraphForm').addClass('hidden');
                $('.graph-execution').addClass('hidden');
                $('#addTimeForm').addClass('hidden');
                $('#serverGroup').addClass("hidden");
            },
            error: function (xhr) {
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
