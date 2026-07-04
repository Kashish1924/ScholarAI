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

    const setButtonBusyState = (button, isBusy, busyText) => {
        if (!button) {
            return;
        }
        if (!button.dataset.originalText) {
            button.dataset.originalText = button.textContent;
        }
        button.disabled = isBusy;
        button.textContent = isBusy ? busyText : button.dataset.originalText;
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

    document.querySelectorAll("[data-copy-text]").forEach((button) => {
        button.addEventListener("click", async () => {
            const copyText = button.dataset.copyText || "";
            try {
                await navigator.clipboard.writeText(copyText);
                const originalText = button.textContent;
                button.textContent = "Copied";
                window.setTimeout(() => {
                    button.textContent = originalText;
                }, 1200);
            } catch (error) {
                window.alert("Unable to copy the text automatically.");
            }
        });
    });

    const chatShell = document.querySelector("[data-ai-chat-shell]");
    const chatForm = document.querySelector("[data-ai-chat-form]");
    const chatStatus = document.querySelector("[data-ai-chat-status]");
    const chatInput = document.querySelector("#aiChatMessage");

    const appendChatMessage = (role, title, body) => {
        if (!chatShell) {
            return;
        }
        const message = document.createElement("div");
        message.className = "glass-card p-4";
        message.innerHTML = `
            <p class="small text-uppercase text-secondary mb-1">${escapeHtml(title)}</p>
            <p class="${role === "user" ? "mb-0" : "mb-2"}">${escapeHtml(body)}</p>
        `;
        chatShell.appendChild(message);
        message.scrollIntoView({ behavior: "smooth", block: "end" });
    };

    if (chatForm && chatInput && chatShell) {
        chatForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const message = chatInput.value.trim();
            const submitButton = chatForm.querySelector("button[type='submit']");
            if (!message) {
                return;
            }

            appendChatMessage("user", "You", message);
            chatInput.value = "";
            setButtonBusyState(submitButton, true, "Sending...");
            if (chatStatus) {
                chatStatus.textContent = "Generating placeholder response...";
            }

            try {
                const response = await fetch("/api/v1/ai/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        message,
                        page_context: "general",
                    }),
                });
                const payload = await response.json();
                const assistantText = payload?.data?.answer || payload?.message || "No response available.";
                appendChatMessage("assistant", "Assistant", assistantText);
                if (chatStatus) {
                    chatStatus.textContent = "Local placeholder mode";
                }
            } catch (error) {
                appendChatMessage(
                    "assistant",
                    "Assistant",
                    "The placeholder assistant could not respond right now. Please try again."
                );
                if (chatStatus) {
                    chatStatus.textContent = "Temporary error";
                }
            } finally {
                setButtonBusyState(submitButton, false, "Sending...");
            }
        });

        document.querySelectorAll("[data-chat-prompt]").forEach((button) => {
            button.addEventListener("click", () => {
                chatInput.value = button.dataset.chatPrompt || "";
                chatInput.focus();
            });
        });
    }

    const searchInput = document.querySelector("[data-search-input]");
    const suggestionPanel = document.querySelector("[data-search-suggestions]");
    let suggestionTimer = null;

    const hideSuggestions = () => {
        if (!suggestionPanel) {
            return;
        }
        suggestionPanel.classList.add("d-none");
        suggestionPanel.innerHTML = "";
    };

    if (searchInput && suggestionPanel) {
        searchInput.addEventListener("input", () => {
            const query = searchInput.value.trim();
            window.clearTimeout(suggestionTimer);
            if (query.length < 2) {
                hideSuggestions();
                return;
            }

            suggestionTimer = window.setTimeout(async () => {
                try {
                    const response = await fetch(`/api/v1/search/suggestions?q=${encodeURIComponent(query)}`);
                    const payload = await response.json();
                    const items = payload?.data || [];
                    if (!items.length) {
                        hideSuggestions();
                        return;
                    }

                    suggestionPanel.innerHTML = items.map((item) => `
                        <button class="suggestion-item" type="button" data-suggestion-label="${escapeHtml(item.label)}">
                            <strong>${escapeHtml(item.label)}</strong>
                            <span class="suggestion-meta">${escapeHtml(item.type)}${item.meta ? ` · ${escapeHtml(item.meta)}` : ""}</span>
                        </button>
                    `).join("");
                    suggestionPanel.classList.remove("d-none");

                    suggestionPanel.querySelectorAll("[data-suggestion-label]").forEach((button) => {
                        button.addEventListener("click", () => {
                            searchInput.value = button.dataset.suggestionLabel || "";
                            hideSuggestions();
                        });
                    });
                } catch (error) {
                    hideSuggestions();
                }
            }, 220);
        });

        document.addEventListener("click", (event) => {
            if (!suggestionPanel.contains(event.target) && event.target !== searchInput) {
                hideSuggestions();
            }
        });
    }

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
