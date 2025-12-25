// WebSocket менеджер для автоматического подключения
class WebSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isPaused = false;
        this.notifications = [];
        this.maxNotifications = 100;

        this.initElements();
        this.initEventListeners();
        this.connect();
    }

    initElements() {
        this.wsStatus = document.getElementById('wsStatus');
        this.statusDot = this.wsStatus.querySelector('.status-dot');
        this.statusText = this.wsStatus.querySelector('.status-text');
        this.notificationsList = document.getElementById('notificationsList');
        this.notificationsCount = document.getElementById('notificationsCount');
        this.clearBtn = document.getElementById('clearNotifications');
        this.pauseBtn = document.getElementById('togglePause');
    }

    initEventListeners() {
        this.clearBtn.addEventListener('click', () => this.clearNotifications());
        this.pauseBtn.addEventListener('click', () => this.togglePause());

        // Автоматическое переподключение при фокусе страницы
        window.addEventListener('focus', () => {
            if (!this.ws || this.ws.readyState === WebSocket.CLOSED) {
                this.reconnect();
            }
        });
    }

    connect() {
        // Если уже подключены или подключаемся - выходим
        if (this.ws && (this.ws.readyState === WebSocket.OPEN ||
                       this.ws.readyState === WebSocket.CONNECTING)) {
            return;
        }

        // Определяем URL WebSocket
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/lesson/`;

        this.updateStatus('connecting', 'Подключение...');

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('✅ WebSocket подключен');
                this.updateStatus('connected', 'Подключено');
                this.reconnectAttempts = 0;
                this.addNotification({
                    type: 'system',
                    title: 'WebSocket подключен',
                    message: 'Соединение установлено успешно',
                    timestamp: new Date()
                });
            };

            this.ws.onmessage = (event) => {
                if (this.isPaused) return;

                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (e) {
                    // Если не JSON, обрабатываем как текст
                    this.handleTextMessage(event.data);
                }
            };

            this.ws.onerror = (error) => {
                console.error('❌ Ошибка WebSocket:', error);
                this.updateStatus('error', 'Ошибка подключения');
            };

            this.ws.onclose = (event) => {
                console.log(`🔌 Соединение закрыто (код: ${event.code})`);
                this.updateStatus('disconnected', 'Отключено');

                // Автопереподключение
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    const delay = Math.min(this.reconnectDelay * this.reconnectAttempts, 10000);

                    setTimeout(() => {
                        console.log(`🔄 Переподключение через ${delay/1000}сек...`);
                        this.connect();
                    }, delay);
                }
            };

        } catch (error) {
            console.error('💥 Ошибка при создании WebSocket:', error);
            this.updateStatus('error', 'Ошибка');
        }
    }

    reconnect() {
        this.reconnectAttempts = 0;
        this.connect();
    }

    updateStatus(status, text) {
        this.statusText.textContent = text;
        this.statusDot.className = 'status-dot ' + status;
        this.wsStatus.setAttribute('data-status', status);
    }

    handleMessage(data) {
        console.log('📥 Получено сообщение:', data);

        // Обработка разных типов сообщений
        if (data.type === 'lesson_created') {
            // Обрабатываем переносы строк в сообщении
            const formattedMessage = this.formatMessageWithLineBreaks(data.message || '');

            this.addNotification({
                type: 'success',
                title: '🎉 Урок создан',
                message: formattedMessage,
                rawMessage: data.message, // Сохраняем оригинальное сообщение
                timestamp: new Date(),
                data: data.lesson
            });
        }
        else if (data.type === 'reminder') {
            const formattedMessage = this.formatMessageWithLineBreaks(data.message || 'Скоро начнется урок');

            this.addNotification({
                type: 'reminder',
                title: '⏰ Напоминание',
                message: formattedMessage,
                rawMessage: data.message,
                timestamp: new Date(),
                data: data
            });
        }
        else if (data.type === 'task_completed') {
            const formattedMessage = this.formatMessageWithLineBreaks(data.message || 'Фоновая задача завершена');

            this.addNotification({
                type: 'info',
                title: '✅ Задача выполнена',
                message: formattedMessage,
                rawMessage: data.message,
                timestamp: new Date(),
                data: data
            });
        }
        else if (data.type === 'error') {
            const formattedMessage = this.formatMessageWithLineBreaks(data.message || 'Произошла ошибка');

            this.addNotification({
                type: 'error',
                title: '❌ Ошибка',
                message: formattedMessage,
                rawMessage: data.message,
                timestamp: new Date(),
                data: data
            });
        }
        else if (data.type === 'notification') {
            // Обработка уведомлений от вашего consumer
            const formattedMessage = this.formatMessageWithLineBreaks(data.message || '');

            this.addNotification({
                type: data.status || 'info',
                title: data.title || '📨 Сообщение',
                message: formattedMessage,
                rawMessage: data.message,
                timestamp: data.timestamp ? new Date(data.timestamp) : new Date(),
                data: data
            });
        }
        else {
            // Общее сообщение
            const message = data.message || JSON.stringify(data);
            const formattedMessage = this.formatMessageWithLineBreaks(message);

            this.addNotification({
                type: 'info',
                title: '📨 Сообщение',
                message: formattedMessage,
                rawMessage: message,
                timestamp: new Date(),
                data: data
            });
        }
    }

    formatMessageWithLineBreaks(message) {
        if (!message) return '';

        // Сохраняем оригинальные переносы строк
        // Заменяем \n на HTML-тег <br> для правильного отображения
        return message
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    handleTextMessage(text) {
        const formattedMessage = this.formatMessageWithLineBreaks(text);

        this.addNotification({
            type: 'info',
            title: '📨 Текст',
            message: formattedMessage,
            rawMessage: text,
            timestamp: new Date()
        });
    }

    addNotification(notification) {
        // Добавляем в массив
        this.notifications.unshift(notification);

        // Ограничиваем количество
        if (this.notifications.length > this.maxNotifications) {
            this.notifications = this.notifications.slice(0, this.maxNotifications);
        }

        // Обновляем интерфейс
        this.renderNotifications();
        this.updateCounter();

        // Автоочистка старых уведомлений
        this.cleanupOldNotifications();
    }

    renderNotifications() {
        // Убираем placeholder если есть
        const placeholder = this.notificationsList.querySelector('.notification-placeholder');
        if (placeholder) {
            placeholder.remove();
        }

        // Очищаем и перерисовываем
        this.notificationsList.innerHTML = '';

        this.notifications.forEach((notification, index) => {
            const notificationElement = this.createNotificationElement(notification, index);
            this.notificationsList.appendChild(notificationElement);
        });
    }

    createNotificationElement(notification, id) {
        const div = document.createElement('div');
        div.className = `notification ${notification.type}`;
        div.dataset.id = id;

        const timeStr = notification.timestamp.toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        // ⭐⭐ ИСПРАВЛЕННАЯ ЧАСТЬ: Добавляем поддержку переносов строк ⭐⭐
        div.innerHTML = `
            <div class="notification-header">
                <div class="notification-title">${notification.title || 'Уведомление'}</div>
                <div class="notification-time">${timeStr}</div>
            </div>
            <div class="notification-body">
                ${notification.message || ''}
            </div>
            <div class="notification-footer">
                <span class="notification-type">${this.getTypeLabel(notification.type)}</span>
                <button class="notification-close" title="Закрыть">×</button>
            </div>
        `;

        // Обработчик закрытия
        div.querySelector('.notification-close').addEventListener('click', () => {
            this.removeNotification(id);
        });

        return div;
    }

    getTypeLabel(type) {
        const labels = {
            'reminder': 'Напоминание',
            'error': 'Ошибка',
            'success': 'Успех',
            'info': 'Инфо',
            'system': 'Система'
        };
        return labels[type] || type;
    }

    removeNotification(id) {
        this.notifications = this.notifications.filter((_, index) => index != id);
        this.renderNotifications();
        this.updateCounter();
    }

    clearNotifications() {
        this.notifications = [];
        this.renderNotifications();
        this.updateCounter();

        // Показываем placeholder
        this.notificationsList.innerHTML = `
            <div class="notification-placeholder">
                <div class="notification-placeholder-icon">✨</div>
                <p>Уведомления очищены</p>
                <small>Ожидание новых сообщений...</small>
            </div>
        `;
    }

    togglePause() {
        this.isPaused = !this.isPaused;
        this.pauseBtn.innerHTML = this.isPaused ? '▶️' : '⏸️';
        this.pauseBtn.title = this.isPaused ? 'Продолжить' : 'Пауза';

        this.addNotification({
            type: 'system',
            title: this.isPaused ? '⏸️ Уведомления на паузе' : '▶️ Уведомления возобновлены',
            message: this.isPaused
                ? 'Новые уведомления не будут показываться'
                : 'Уведомления снова активны',
            timestamp: new Date()
        });
    }

    updateCounter() {
        this.notificationsCount.textContent = this.notifications.length;
    }

    cleanupOldNotifications() {
        const now = new Date();
        const hourAgo = now.getTime() - (60 * 60 * 1000); // 1 час

        this.notifications = this.notifications.filter(notification => {
            return notification.timestamp.getTime() > hourAgo;
        });
    }

    // Отправка сообщения (если понадобится)
    sendMessage(data) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            console.warn('WebSocket не подключен');
            return false;
        }

        const message = typeof data === 'string' ? data : JSON.stringify(data);
        this.ws.send(message);
        console.log('📤 Отправлено:', message);
        return true;
    }
}

// Автоматическая инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Проверяем, есть ли контейнер уведомлений на странице
    if (document.getElementById('notificationsList')) {
        // Загружаем CSS если еще не загружен
        if (!document.querySelector('link[href*="notifications.css"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = '/static/css/notifications.css';
            document.head.appendChild(link);
        }

        // Создаем экземпляр WebSocketManager
        window.wsManager = new WebSocketManager();

        // Для отладки - выводим в глобальную область видимости
        console.log('🚀 WebSocketManager инициализирован');
    }
});