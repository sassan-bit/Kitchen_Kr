// static/js/favorites.js

document.addEventListener('DOMContentLoaded', function() {
    // ==================== ОБРАБОТКА ИЗБРАННОГО ====================
    
    // Обработчик для всех кнопок избранного
    document.addEventListener('click', function(e) {
        const favoriteBtn = e.target.closest('[data-favorite-action]');
        if (!favoriteBtn) return;
        
        e.preventDefault();
        handleFavoriteAction(favoriteBtn);
    });
    
    // Обработчик для быстрого добавления при нажатии на само сердечко
    document.addEventListener('click', function(e) {
        const heartIcon = e.target.closest('.js-favorite-heart, .favorite-icon, .heart-icon');
        if (!heartIcon) return;
        
        e.preventDefault();
        const favoriteBtn = heartIcon.closest('[data-favorite-action]');
        if (favoriteBtn) {
            handleFavoriteAction(favoriteBtn);
        }
    });
    
    // ==================== ФУНКЦИЯ ОБРАБОТКИ ИЗБРАННОГО ====================
    async function handleFavoriteAction(button) {
        const kitchenId = button.dataset.kitchenId;
        const isAuthenticated = button.dataset.isAuthenticated === 'true';
        const loginUrl = button.dataset.loginUrl;
        const action = button.dataset.favoriteAction || 'toggle';
        
        // Проверка авторизации
        if (!isAuthenticated) {
            window.location.href = loginUrl;
            return;
        }
        
        // Блокируем кнопку на время запроса
        button.disabled = true;
        const originalHTML = button.innerHTML;
        
        try {
            // Показываем индикатор загрузки
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            const response = await fetch(`/accounts/favorites/${action}/${kitchenId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/json'
                },
                body: action === 'update-note' ? JSON.stringify({
                    note: button.dataset.note
                }) : null
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Обработка успешного ответа
            if (data.status === 'success') {
                updateFavoriteUI(button, data);
                showNotification(data.message || getActionMessage(data.action, data.kitchen_name), 'success');
                
                // Обновляем счетчик в шапке
                updateHeaderCounter(data.total_favorites);
            }
            
        } catch (error) {
            console.error('Favorite action error:', error);
            showNotification('Произошла ошибка. Попробуйте еще раз.', 'error');
            
            // Восстанавливаем исходное состояние кнопки
            button.innerHTML = originalHTML;
            button.disabled = false;
        }
    }
    
    // ==================== ОБНОВЛЕНИЕ ИНТЕРФЕЙСА ====================
    function updateFavoriteUI(button, data) {
        const { action, is_favorite, kitchen_id } = data;
        
        // Обновляем состояние кнопки
        if (action === 'added' || is_favorite) {
            button.classList.add('active', 'favorited');
            button.dataset.isFavorite = 'true';
            button.title = 'Удалить из избранного';
            
            // Обновляем иконку
            const icon = button.querySelector('.favorite-icon, .js-favorite-icon');
            if (icon) {
                icon.classList.remove('far', 'fa-heart');
                icon.classList.add('fas', 'fa-heart');
            }
            
            // Обновляем текст если есть
            const text = button.querySelector('.favorite-text, .js-favorite-text');
            if (text) {
                text.textContent = 'В избранном';
            }
            
            // Показываем бейдж если есть
            const badge = document.getElementById(`favorite-badge-${kitchen_id}`);
            if (badge) {
                badge.classList.add('visible');
                badge.style.display = 'block';
            }
            
        } else {
            button.classList.remove('active', 'favorited');
            button.dataset.isFavorite = 'false';
            button.title = 'Добавить в избранное';
            
            // Обновляем иконку
            const icon = button.querySelector('.favorite-icon, .js-favorite-icon');
            if (icon) {
                icon.classList.remove('fas', 'fa-heart');
                icon.classList.add('far', 'fa-heart');
            }
            
            // Обновляем текст если есть
            const text = button.querySelector('.favorite-text, .js-favorite-text');
            if (text) {
                text.textContent = 'В избранное';
            }
            
            // Скрываем бейдж если есть
            const badge = document.getElementById(`favorite-badge-${kitchen_id}`);
            if (badge) {
                badge.classList.remove('visible');
                badge.style.display = 'none';
            }
        }
        
        // Восстанавливаем кнопку
        button.disabled = false;
        
        // Если есть специальный обработчик для обновления, вызываем его
        if (window.favoriteUpdated) {
            window.favoriteUpdated(data);
        }
    }
    
    // ==================== ПРОВЕРКА СТАТУСА ИЗБРАННОГО ====================
    async function checkFavoriteStatus(kitchenId) {
        try {
            const response = await fetch(`/accounts/api/check-favorite/${kitchenId}/`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Check favorite status error:', error);
        }
        return { is_favorite: false };
    }
    
    // ==================== ЗАГРУЗКА СЧЕТЧИКА ИЗБРАННОГО ====================
    async function loadFavoritesCounter() {
        try {
            const response = await fetch('/accounts/api/favorites-count/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                updateHeaderCounter(data.count);
            }
        } catch (error) {
            console.error('Load favorites counter error:', error);
        }
    }
    
    // ==================== ОБНОВЛЕНИЕ СЧЕТЧИКА В ШАПКЕ ====================
    function updateHeaderCounter(count) {
        // Ищем все счетчики избранного на странице
        const counters = document.querySelectorAll('.favorites-count, .js-favorites-count, .header__favorites-count');
        
        counters.forEach(counter => {
            const oldCount = parseInt(counter.textContent) || 0;
            counter.textContent = count;
            
            // Анимация при изменении
            if (count !== oldCount) {
                counter.classList.add('updated');
                setTimeout(() => counter.classList.remove('updated'), 300);
            }
        });
        
        // Обновляем title для иконки
        const favoriteIcons = document.querySelectorAll('.header-favorites-link');
        favoriteIcons.forEach(icon => {
            icon.title = `Избранное (${count})`;
        });
    }
    
    // ==================== УПРАВЛЕНИЕ ЗАМЕТКАМИ ====================
    document.addEventListener('click', function(e) {
        const editNoteBtn = e.target.closest('.edit-note-btn');
        if (!editNoteBtn) return;
        
        e.preventDefault();
        const favoriteId = editNoteBtn.dataset.favoriteId;
        showNoteEditor(favoriteId, editNoteBtn.dataset.currentNote || '');
    });
    
    function showNoteEditor(favoriteId, currentNote = '') {
        const modalHTML = `
            <div class="modal-overlay favorite-note-modal" id="noteModal-${favoriteId}">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Редактировать заметку</h3>
                        <button class="modal-close">&times;</button>
                    </div>
                    <div class="modal-body">
                        <textarea class="note-textarea" rows="4" 
                                  placeholder="Добавьте заметку об этом товаре...">${currentNote}</textarea>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary cancel-note">Отмена</button>
                        <button class="btn btn-primary save-note" data-favorite-id="${favoriteId}">
                            Сохранить
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Удаляем предыдущее модальное окно если есть
        const existingModal = document.getElementById(`noteModal-${favoriteId}`);
        if (existingModal) existingModal.remove();
        
        // Добавляем новое
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Обработчики для модального окна
        const modal = document.getElementById(`noteModal-${favoriteId}`);
        
        modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
        modal.querySelector('.cancel-note').addEventListener('click', () => modal.remove());
        
        modal.querySelector('.save-note').addEventListener('click', async function() {
            const note = modal.querySelector('.note-textarea').value.trim();
            const favoriteId = this.dataset.favoriteId;
            
            try {
                const response = await fetch(`/accounts/favorites/update-note/${favoriteId}/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCsrfToken(),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ note: note })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    // Обновляем отображение заметки на странице
                    const noteElement = document.querySelector(`.favorite-note[data-favorite-id="${favoriteId}"]`);
                    if (noteElement) {
                        noteElement.textContent = note || 'Добавить заметку...';
                    }
                    
                    showNotification('Заметка сохранена', 'success');
                    modal.remove();
                }
            } catch (error) {
                console.error('Save note error:', error);
                showNotification('Ошибка сохранения заметки', 'error');
            }
        });
        
        // Закрытие по клику вне модального окна
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                modal.remove();
            }
        });
    }
    
    // ==================== УДАЛЕНИЕ ИЗ ИЗБРАННОГО ====================
    document.addEventListener('click', function(e) {
        const removeBtn = e.target.closest('.remove-favorite-btn');
        if (!removeBtn) return;
        
        e.preventDefault();
        const favoriteId = removeBtn.dataset.favoriteId;
        const kitchenName = removeBtn.dataset.kitchenName || 'этот товар';
        
        if (confirm(`Вы уверены, что хотите удалить "${kitchenName}" из избранного?`)) {
            removeFavorite(favoriteId);
        }
    });
    
    async function removeFavorite(favoriteId) {
        try {
            const response = await fetch(`/accounts/favorites/remove/${favoriteId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Удаляем элемент из DOM
                const favoriteElement = document.querySelector(`.favorite-item[data-favorite-id="${favoriteId}"]`);
                if (favoriteElement) {
                    favoriteElement.remove();
                }
                
                showNotification(data.message || 'Товар удален из избранного', 'success');
                updateHeaderCounter(data.total_favorites);
                
                // Если страница пустая, показываем сообщение
                const favoriteList = document.querySelector('.favorites-list');
                if (favoriteList && favoriteList.children.length === 0) {
                    favoriteList.innerHTML = `
                        <div class="empty-favorites">
                            <i class="far fa-heart"></i>
                            <p>Ваш список избранного пуст</p>
                            <a href="/catalog/" class="btn btn-primary">Перейти в каталог</a>
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Remove favorite error:', error);
            showNotification('Ошибка удаления товара', 'error');
        }
    }
    
    // ==================== ПОЛУЧЕНИЕ CSRF-ТОКЕНА ====================
    function getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        // Если используется Django's CSRF token в meta теге
        if (!cookieValue) {
            const metaToken = document.querySelector('meta[name="csrf-token"]');
            if (metaToken) {
                return metaToken.getAttribute('content');
            }
        }
        
        return cookieValue || '';
    }
    
    // ==================== ФУНКЦИЯ УВЕДОМЛЕНИЙ ====================
    function showNotification(message, type = 'info') {
        // Удаляем предыдущие уведомления
        const oldNotifications = document.querySelectorAll('.notification:not(.notification-static)');
        oldNotifications.forEach(notification => {
            if (!notification.classList.contains('notification-static')) {
                notification.remove();
            }
        });
        
        // Создаем новое уведомление
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="notification-icon ${getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">&times;</button>
        `;
        
        document.body.appendChild(notification);
        
        // Показываем уведомление
        setTimeout(() => notification.classList.add('show'), 10);
        
        // Автоматическое скрытие
        const autoHide = setTimeout(() => {
            hideNotification(notification);
        }, 5000);
        
        // Закрытие по клику
        notification.querySelector('.notification-close').addEventListener('click', () => {
            clearTimeout(autoHide);
            hideNotification(notification);
        });
    }
    
    function hideNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }
    
    function getNotificationIcon(type) {
        const icons = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }
    
    function getActionMessage(action, kitchenName) {
        const messages = {
            'added': `"${kitchenName}" добавлен в избранное`,
            'removed': `"${kitchenName}" удален из избранного`,
            'updated': 'Избранное обновлено'
        };
        return messages[action] || 'Действие выполнено';
    }
    
    // ==================== ИНИЦИАЛИЗАЦИЯ ====================
    function initFavorites() {
        // Загружаем счетчик избранного при загрузке страницы
        loadFavoritesCounter();
        
        // Инициализируем все кнопки избранного
        document.querySelectorAll('[data-favorite-action]').forEach(button => {
            const kitchenId = button.dataset.kitchenId;
            if (kitchenId && button.dataset.isAuthenticated === 'true') {
                // Проверяем статус избранного для каждой кнопки
                checkFavoriteStatus(kitchenId).then(data => {
                    if (data.is_favorite && !button.classList.contains('active')) {
                        updateFavoriteUI(button, {
                            action: 'added',
                            is_favorite: true,
                            kitchen_id: kitchenId
                        });
                    }
                });
            }
        });
    }
    
    // Запуск инициализации
    initFavorites();
    
    // Экспортируем функции для глобального использования
    window.FavoritesAPI = {
        toggle: handleFavoriteAction,
        checkStatus: checkFavoriteStatus,
        updateCounter: updateHeaderCounter,
        showNotification: showNotification,
        editNote: showNoteEditor,
        remove: removeFavorite
    };
});

// Добавляем CSS для уведомлений и модальных окон
const favoriteStyles = `
<style>
/* Уведомления */
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    padding: 16px 20px;
    min-width: 300px;
    max-width: 400px;
    z-index: 9999;
    transform: translateX(150%);
    transition: transform 0.3s ease;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-left: 4px solid #007bff;
}

.notification.show {
    transform: translateX(0);
}

.notification-success {
    border-left-color: #28a745;
}

.notification-error {
    border-left-color: #dc3545;
}

.notification-warning {
    border-left-color: #ffc107;
}

.notification-info {
    border-left-color: #17a2b8;
}

.notification-content {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
}

.notification-icon {
    font-size: 18px;
}

.notification-success .notification-icon {
    color: #28a745;
}

.notification-error .notification-icon {
    color: #dc3545;
}

.notification-warning .notification-icon {
    color: #ffc107;
}

.notification-info .notification-icon {
    color: #17a2b8;
}

.notification-close {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: #6c757d;
    padding: 0;
    margin-left: 10px;
    line-height: 1;
}

.notification-close:hover {
    color: #343a40;
}

/* Модальные окна */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    animation: fadeIn 0.3s ease;
}

.modal-content {
    background: white;
    border-radius: 12px;
    max-width: 500px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    animation: slideUp 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideUp {
    from { 
        opacity: 0;
        transform: translateY(20px);
    }
    to { 
        opacity: 1;
        transform: translateY(0);
    }
}

.modal-header {
    padding: 20px;
    border-bottom: 1px solid #dee2e6;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h3 {
    margin: 0;
    font-size: 1.25rem;
}

.modal-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #6c757d;
    line-height: 1;
}

.modal-close:hover {
    color: #343a40;
}

.modal-body {
    padding: 20px;
}

.note-textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #ced4da;
    border-radius: 6px;
    font-family: inherit;
    font-size: 14px;
    resize: vertical;
}

.note-textarea:focus {
    outline: none;
    border-color: #80bdff;
    box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}

.modal-footer {
    padding: 20px;
    border-top: 1px solid #dee2e6;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

/* Анимация счетчика */
.favorites-count.updated {
    animation: countUpdate 0.3s ease;
}

@keyframes countUpdate {
    0% { transform: scale(1); }
    50% { transform: scale(1.3); }
    100% { transform: scale(1); }
}

/* Состояния кнопки избранного */
[data-favorite-action].loading {
    opacity: 0.7;
    cursor: wait;
}

[data-favorite-action].active .favorite-icon {
    color: #dc3545 !important;
}

/* Пустой список избранного */
.empty-favorites {
    text-align: center;
    padding: 60px 20px;
}

.empty-favorites i {
    font-size: 64px;
    color: #dee2e6;
    margin-bottom: 20px;
}

.empty-favorites p {
    color: #6c757d;
    font-size: 18px;
    margin-bottom: 20px;
}
</style>
`;

// Добавляем стили в документ
document.head.insertAdjacentHTML('beforeend', favoriteStyles);