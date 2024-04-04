function checkForUpdates() {
    $.ajax({
        url: '/node_metrics',
        type: 'GET',
        success: function(data) {
            var timestamp = $(data).find('#timestamp').text()

            if (timestamp == $('#timestamp').text()) {
                setTimeout(checkForUpdates, 20000)
                return
            }

            $('.update').each(function() {
                var id = $(this).attr('id')
                var updated_data = $(data).find('#' + id).html()
                $(this).html(updated_data)
            })

            var date_string = timestamp.substring(27)
            var target_time = new Date(date_string)
            target_time.setMinutes(target_time.getMinutes() + 1)
            target_time.setSeconds(target_time.getSeconds() + 5)

            var current_time = Date.now()
            var next_update = target_time.getTime() - current_time

            if (next_update <= 0) {
                next_update = 20000
            }
            setTimeout(checkForUpdates, next_update)
        }
    })
}

$(document).ready(function() {
    checkForUpdates()
})
