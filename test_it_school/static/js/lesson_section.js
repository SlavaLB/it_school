const lessonsList = document.getElementById("lessonsList");
const prevBtn = document.getElementById("prevPage");
const nextBtn = document.getElementById("nextPage");
const pageInfo = document.getElementById("pageInfo");

let currentPage = 1;
let totalPages = 1;

async function loadLessons(page = 1) {
    lessonsList.innerHTML = "";

    const response = await fetch(`/lessons/?page=${page}`);
    const data = await response.json();

    const lessons = data.items; // теперь берем items
    totalPages = data.pagination.pages;

    lessons.forEach(lesson => {
        const card = document.createElement("div");
        card.className = "lesson-card";
        card.innerHTML = `
            <h3>${lesson.title}</h3>
            <p>${lesson.description || "Без описания"}</p>
            <div class="lesson-meta">
                ${lesson.start_time} • ${lesson.status}
            </div>
        `;
        lessonsList.appendChild(card);
    });

    // Обновляем пагинацию
    pageInfo.textContent = `Страница ${data.pagination.page} из ${data.pagination.pages}`;
    prevBtn.disabled = !data.pagination.has_prev;
    nextBtn.disabled = !data.pagination.has_next;

    currentPage = page;
}

// обработчики кнопок
prevBtn.addEventListener("click", () => loadLessons(currentPage - 1));
nextBtn.addEventListener("click", () => loadLessons(currentPage + 1));

// загрузка первой страницы
loadLessons();
