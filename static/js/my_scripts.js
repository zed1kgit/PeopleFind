$(document).ready(function() {
    $('.subscribe').on('click', function(event) {
        event.preventDefault(); // Предотвращаем стандартную обработку ссылки

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
            success: function(response) {
                if (response.success) {
                    if (isSubscribed === true) {
                        $this.text('Подписаться');
                        $this.data('is-subscribed', false); // Меняем значение атрибута данных
                        $this.removeClass('btn-danger').addClass('btn-success')
                    } else {
                        $this.text('Отписаться');
                        $this.data('is-subscribed', true); // Меняем значение атрибута данных
                        $this.removeClass('btn-success').addClass('btn-danger')
                    }
                } else {
                    alert('Произошла ошибка.');
                }
            },
            error: function(xhr, status, error) {
                console.error('Ошибка:', xhr.statusText);
            }
        });
    });
});