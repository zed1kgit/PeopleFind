$(document).ready(function () {
    $('.subscribe').on('click', function (event) {
        event.preventDefault();

        let $this = $(this);
        let interestId = $this.data('interest-id');
        let isSubscribed = $this.data('is-subscribed');
        let url = $this.data('url');

        $.ajax({
            type: 'POST',
            url: url,
            data: {
                interest_id: interestId,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (response) {
                if (response.success) {
                    if (isSubscribed === true) {
                        $this.text('Подписаться');
                        $this.data('is-subscribed', false);
                        $this.removeClass('btn-danger').addClass('btn-success')
                    } else {
                        $this.text('Отписаться');
                        $this.data('is-subscribed', true);
                        $this.removeClass('btn-success').addClass('btn-danger')
                    }
                } else {
                    alert('Произошла ошибка.');
                }
            },
            error: function (xhr, status, error) {
                console.error('Ошибка:', xhr.statusText);
            }
        });
    });

    let area = $('.area');

    area.on('click', function (event) {
        event.preventDefault();

        let $this = $(this);
        let url = $this.data('url');
        let userId = $this.data('user-id')

        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'user-id': userId,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (response) {
                if (response.success) {
                    if (response.new_object_id === 'none') {
                        window.location.href = '/interests/user-found'
                    } else {
                        updateUserDetail(response.new_object, response.new_object_id);
                    }
                } else {
                    alert(response.message);
                }
            },
            error: function (xhr, status, error) {
                console.error('Ошибка:', status, error);
            }
        });
    });

    function updateUserDetail(newObjectHtml, objectId) {
        $('#user-detail').html(newObjectHtml);
        area.each(function (_, el) {
            $(el).data('user-id', objectId)
            $(el).attr('data-user-id', objectId)
        });
    }

    $('.new-marker').on('click', function () {
        let $this = $(this)
        let notificationId = $this.data('id');
        $.ajax({
            url: "/mark_as_read/0/".replace('0', notificationId),
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    $this.addClass('off');
                } else {
                    alert('Произошла ошибка при отметке уведомления как прочитанного.');
                }
            },
            error: function(xhr, textStatus, errorThrown) {
                console.error(textStatus + ': ' + errorThrown);
            }
        });
    });
});

