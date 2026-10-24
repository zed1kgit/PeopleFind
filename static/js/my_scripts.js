/*
 * Скрипты PeopleFind без jQuery: fetch + data-атрибуты.
 * Адреса запросов берутся из data-url в разметке, чтобы не дублировать маршруты Django.
 */
(function () {
    'use strict';

    const csrfToken = (document.querySelector('meta[name="csrf-token"]') || {}).content || '';

    function showError(message) {
        const toast = document.createElement('div');
        toast.className = 'toast-error';
        toast.setAttribute('role', 'alert');
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    async function post(url, data) {
        const body = new URLSearchParams();
        Object.entries(data || {}).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                body.append(key, value);
            }
        });
        const response = await fetch(url, {
            method: 'POST',
            headers: {'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest'},
            body: body,
            credentials: 'same-origin',
        });
        let payload = {};
        try {
            payload = await response.json();
        } catch (error) {
            // ответ без JSON: ниже сработает проверка response.ok
        }
        if (!response.ok || payload.success === false) {
            throw new Error(payload.error || 'Произошла ошибка. Попробуйте еще раз.');
        }
        return payload;
    }

    // Элементы-"кнопки" (span, a без href) должны работать и с клавиатуры
    document.querySelectorAll('[role="button"]:not(button)').forEach((element) => {
        element.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                element.click();
            }
        });
    });

    // --- Подписка на интерес ------------------------------------------------
    function setSubscribed(button, subscribed) {
        button.textContent = subscribed ? 'Отписаться' : 'Подписаться';
        button.classList.toggle('btn-danger', subscribed);
        button.classList.toggle('btn-success', !subscribed);
        button.dataset.isSubscribed = String(subscribed);
    }

    document.querySelectorAll('.subscribe').forEach((button) => {
        button.addEventListener('click', async (event) => {
            event.preventDefault();
            button.disabled = true;
            try {
                const data = await post(button.dataset.url);
                setSubscribed(button, data.subscribed);
                document.querySelectorAll('[data-members-for="' + button.dataset.interestId + '"]')
                    .forEach((element) => { element.textContent = data.members_count; });
            } catch (error) {
                showError(error.message);
            } finally {
                button.disabled = false;
            }
        });
    });

    // --- Поиск людей: одобрить / отклонить ----------------------------------
    const areas = document.querySelectorAll('.area');
    let ratingInProgress = false;

    areas.forEach((area) => {
        area.addEventListener('click', async (event) => {
            event.preventDefault();
            if (ratingInProgress) {
                return;
            }
            ratingInProgress = true;
            try {
                const data = await post(area.dataset.url, {'user-id': area.dataset.userId});
                if (data.new_object_id === 'none') {
                    window.location.href = document.querySelector('.choose').dataset.foundUrl;
                    return;
                }
                document.getElementById('user-detail').innerHTML = data.new_object;
                areas.forEach((element) => { element.dataset.userId = data.new_object_id; });
            } catch (error) {
                showError(error.message);
            } finally {
                ratingInProgress = false;
            }
        });
    });

    // --- Уведомления ---------------------------------------------------------
    document.querySelectorAll('.new-marker').forEach((marker) => {
        marker.addEventListener('click', async () => {
            if (marker.classList.contains('off')) {
                return;
            }
            try {
                await post(marker.dataset.url);
                marker.classList.add('off');
                const badge = document.querySelector('.menu-icon.notifications');
                if (badge) {
                    badge.dataset.count = Math.max(0, parseInt(badge.dataset.count || '0', 10) - 1);
                }
            } catch (error) {
                showError(error.message);
            }
        });
    });

    // --- Комментарии ---------------------------------------------------------
    const commentForm = document.getElementById('comment_form');
    if (commentForm) {
        const textarea = commentForm.querySelector('textarea');

        commentForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const text = textarea.value.trim();
            if (!text) {
                return;
            }
            const isInterest = commentForm.dataset.type === 'interest';
            try {
                await post(commentForm.dataset.url, {
                    text: text,
                    interest: isInterest ? commentForm.dataset.id : null,
                    topic: isInterest ? null : commentForm.dataset.id,
                });
                window.location.reload();
            } catch (error) {
                showError(error.message);
            }
        });

        textarea.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                commentForm.requestSubmit();
            }
        });
    }

    // --- Удаление комментариев и топиков ------------------------------------
    document.querySelectorAll('.item-delete').forEach((button) => {
        button.addEventListener('click', async (event) => {
            event.preventDefault();
            if (!confirm('Вы уверены, что хотите это удалить?')) {
                return;
            }
            const type = button.dataset.type;   // 'comment' или 'topic'
            const id = button.dataset.id;
            try {
                await post(button.dataset.url, {[type]: id});
                const element = document.getElementById(type + '-' + id);
                if (element) {
                    element.remove();
                }
            } catch (error) {
                showError(error.message);
            }
        });
    });
})();
