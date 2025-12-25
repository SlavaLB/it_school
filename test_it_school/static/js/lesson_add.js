document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('lesson-form');
    const message = document.getElementById('lesson-form-message');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);

        try {
            const response = await fetch('/lesson_add/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: formData
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.errors ? JSON.stringify(data.errors) : 'Ошибка при сохранении урока');
            }

            message.textContent = 'Урок успешно добавлен';
            message.style.color = 'green';
            form.reset();

            // обновляем список уроков, первую страницу
            loadLessons(1);

        } catch (err) {
            message.textContent = err.message;
            message.style.color = 'red';
        }
    });
});

// Django CSRF helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
