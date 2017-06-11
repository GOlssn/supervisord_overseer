/**
 * Created by gustav on 2017-06-08.
 */

$(document).ready(function () {

    $('.startProcess').click(function (e) {
        e.preventDefault();

        var $element = $(this);

        var data = {
            node: $element.data('node'),
            process_name: $element.data('name'),
            group: $element.data('group')
        };
        console.log(data)

        $.ajax({
            url: '/ajax/restart_process',
            data: data,
            dataType: 'json',
            success: function (data) {
                if (data.success == true) {
                    toastr.options.timeOut = 3000;
                    toastr.options.positionClass = "toast-bottom-center";
                    toastr.success(data.message);
                    $element.parent().parent().find('.state').text(data.state);
                } else {
                    toastr.options.timeOut = 3000;
                    toastr.options.positionClass = "toast-bottom-center";
                    toastr.error('Error: ' + data.message);
                }
            },
            type: 'POST'
        });
    });

    $('.stopProcess').click(function (e) {
        e.preventDefault();

        var $element = $(this);

        var data = {
            node: $element.data('node'),
            process_name: $element.data('name'),
            group: $element.data('group')
        };

        console.log(data)

        $.ajax({
            url: '/ajax/stop_process',
            data: data,
            dataType: 'json',
            success: function (data) {
                if (data.success == true) {
                    toastr.options.timeOut = 3000;
                    toastr.options.positionClass = "toast-bottom-center";
                    toastr.success(data.message);
                    $element.parent().parent().find('.state').text(data.state);
                } else {
                    toastr.options.timeOut = 3000;
                    toastr.options.positionClass = "toast-bottom-center";
                    toastr.error('Error: ' + data.message);
                }
            },
            type: 'POST'
        });
    });
});