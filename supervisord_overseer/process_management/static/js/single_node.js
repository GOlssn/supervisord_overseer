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

        $.ajax({
            url: '/ajax/restart_process',
            data: data,
            dataType: 'json',
            success: function (data) {
                if (data.success == true) {
                    toastr.options.timeOut = 3000;
                    toastr.options.positionClass = "toast-bottom-center";
                    toastr.success(data.message);

                    var $label = $element.parent().parent().find('.state').find('span');

                    $label.removeClass('label-success');
                    $label.removeClass('label-danger');
                    $label.removeClass('label-warning');

                    if(data.state == 'RUNNING')
                        $label.addClass('label-success');
                    else if(data.state == 'FATAL')
                        $label.addClass('label-danger');
                    else
                        $label.addClass('label-warning');
                    $label.text(data.state);
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

        $.ajax({
            url: '/ajax/stop_process',
            data: data,
            dataType: 'json',
            success: function (data) {
                if (data.success == true) {
                    toastr.options.timeOut = 3000;
                    toastr.options.positionClass = "toast-bottom-center";
                    toastr.success(data.message);

                    var $label = $element.parent().parent().find('.state').find('span');

                    $label.removeClass('label-success');
                    $label.removeClass('label-danger');
                    $label.removeClass('label-warning');

                    if(data.state == 'RUNNING')
                        $label.addClass('label-success');
                    else if(data.state == 'FATAL')
                        $label.addClass('label-danger');
                    else
                        $label.addClass('label-warning');
                    $label.text(data.state);
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