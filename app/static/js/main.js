document.addEventListener("DOMContentLoaded", () => {
    const BOOKMARKS_KEY = "scholarai_bookmarks";
    const COMPARE_KEY = "scholarai_compare";
    const THEME_KEY = "scholarai_theme";

    const safeRead = (key) => {
        try {
            return JSON.parse(localStorage.getItem(key) || "[]");
        } catch (error) {
            return [];
        }
    };

    const saveList = (key, value) => {
        localStorage.setItem(key, JSON.stringify(value));
    };

    const escapeHtml = (value) => String(value || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");

    const getCardData = (element) => ({
        scholarship_id: Number(element.dataset.scholarshipId),
        scholarship_name: element.dataset.scholarshipName,
        slug: element.dataset.scholarshipSlug,
        provider_name: element.dataset.scholarshipProvider,
        scholarship_amount: element.dataset.scholarshipAmount,
        application_end_date: element.dataset.scholarshipDeadline,
        scholarship_type: element.dataset.scholarshipType,
        degree: element.dataset.scholarshipDegree,
        branch: element.dataset.scholarshipBranch,
    });

    const bookmarks = safeRead(BOOKMARKS_KEY);
    const compareList = safeRead(COMPARE_KEY);

    const isBookmarked = (id) => bookmarks.some((item) => item.scholarship_id === id);
    const isCompared = (id) => compareList.some((item) => item.scholarship_id === id);

    const syncBookmarkButtons = () => {
        document.querySelectorAll("[data-bookmark-toggle]").forEach((button) => {
            const card = button.closest("[data-scholarship-card]");
            if (!card) {
                return;
            }
            const active = isBookmarked(Number(card.dataset.scholarshipId));
            button.classList.toggle("is-active", active);
            const icon = button.querySelector("i");
            if (icon) {
                icon.className = active ? "bi bi-bookmark-fill" : "bi bi-bookmark";
            }
        });
    };

    const syncCompareButtons = () => {
        document.querySelectorAll("[data-compare-toggle]").forEach((button) => {
            const card = button.closest("[data-scholarship-card]");
            if (!card) {
                return;
            }
            const active = isCompared(Number(card.dataset.scholarshipId));
            button.classList.toggle("is-active", active);
            button.textContent = active ? "Selected" : "Compare";
        });

        const countElement = document.querySelector("[data-compare-count]");
        const linkElement = document.querySelector("[data-compare-link]");
        if (countElement) {
            countElement.textContent = String(compareList.length);
        }
        if (linkElement) {
            if (compareList.length > 0) {
                linkElement.classList.remove("disabled");
                linkElement.href = `/student/compare?ids=${compareList.map((item) => item.scholarship_id).join(",")}`;
            } else {
                linkElement.classList.add("disabled");
                linkElement.href = "/student/compare";
            }
        }
    };

    document.querySelectorAll("[data-bookmark-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const card = button.closest("[data-scholarship-card]");
            if (!card) {
                return;
            }
            const item = getCardData(card);
            const existingIndex = bookmarks.findIndex((entry) => entry.scholarship_id === item.scholarship_id);
            if (existingIndex >= 0) {
                bookmarks.splice(existingIndex, 1);
            } else {
                bookmarks.unshift(item);
            }
            saveList(BOOKMARKS_KEY, bookmarks);
            syncBookmarkButtons();
            renderBookmarksPage();
        });
    });

    document.querySelectorAll("[data-compare-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const card = button.closest("[data-scholarship-card]");
            if (!card) {
                return;
            }
            const item = getCardData(card);
            const existingIndex = compareList.findIndex((entry) => entry.scholarship_id === item.scholarship_id);
            if (existingIndex >= 0) {
                compareList.splice(existingIndex, 1);
            } else if (compareList.length < 3) {
                compareList.push(item);
            } else {
                window.alert("You can compare up to 3 scholarships at a time.");
            }
            saveList(COMPARE_KEY, compareList);
            syncCompareButtons();
        });
    });

    const renderBookmarksPage = () => {
        const grid = document.querySelector("[data-bookmarks-grid]");
        const emptyState = document.querySelector("[data-bookmarks-empty]");
        if (!grid || !emptyState) {
            return;
        }

        grid.innerHTML = "";
        if (bookmarks.length === 0) {
            emptyState.classList.remove("d-none");
            return;
        }

        emptyState.classList.add("d-none");
        bookmarks.forEach((item) => {
            const column = document.createElement("div");
            column.className = "col-md-6 col-xl-4";
            column.innerHTML = `
                <article class="scholarship-card h-100">
                    <div class="card-shell h-100 p-4">
                        <div class="d-flex justify-content-between align-items-start gap-3 mb-3">
                            <div>
                                <span class="badge rounded-pill card-badge text-capitalize">${escapeHtml(item.scholarship_type)}</span>
                                <h3 class="h5 mt-3 mb-1">
                                    <a class="text-decoration-none text-white" href="/student/scholarships/${encodeURIComponent(item.slug)}">${escapeHtml(item.scholarship_name)}</a>
                                </h3>
                                <p class="small text-secondary mb-0">${escapeHtml(item.provider_name)}</p>
                            </div>
                            <button class="icon-toggle is-active" type="button" data-remove-bookmark="${item.scholarship_id}">
                                <i class="bi bi-bookmark-fill"></i>
                            </button>
                        </div>
                        <div class="d-flex flex-wrap gap-2 mb-3">
                            <span class="meta-pill">${escapeHtml(item.degree)}</span>
                            <span class="meta-pill">${escapeHtml(item.branch)}</span>
                        </div>
                        <div class="info-grid mt-auto">
                            <div>
                                <span class="info-label">Amount</span>
                                <span class="info-value">${escapeHtml(item.scholarship_amount || "Varies")}</span>
                            </div>
                            <div>
                                <span class="info-label">Deadline</span>
                                <span class="info-value">${escapeHtml(item.application_end_date || "TBA")}</span>
                            </div>
                        </div>
                    </div>
                </article>
            `;
            grid.appendChild(column);
        });

        grid.querySelectorAll("[data-remove-bookmark]").forEach((button) => {
            button.addEventListener("click", () => {
                const id = Number(button.dataset.removeBookmark);
                const existingIndex = bookmarks.findIndex((entry) => entry.scholarship_id === id);
                if (existingIndex >= 0) {
                    bookmarks.splice(existingIndex, 1);
                    saveList(BOOKMARKS_KEY, bookmarks);
                    syncBookmarkButtons();
                    renderBookmarksPage();
                }
            });
        });
    };

    const themeToggle = document.querySelector("[data-theme-toggle]");
    const applyTheme = (theme) => {
        document.body.setAttribute("data-theme", theme);
    };

    const savedTheme = localStorage.getItem(THEME_KEY) || "dark";
    applyTheme(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            const nextTheme = document.body.getAttribute("data-theme") === "light" ? "dark" : "light";
            applyTheme(nextTheme);
            localStorage.setItem(THEME_KEY, nextTheme);
        });
    }

    syncBookmarkButtons();
    syncCompareButtons();
    renderBookmarksPage();
});
