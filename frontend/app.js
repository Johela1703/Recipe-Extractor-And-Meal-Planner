document.addEventListener("DOMContentLoaded", () => {
    const API_BASE = window.location.origin;

    let savedRecipesList = [];
    let selectedRecipeIds = [];

    // UI References
    const tabs = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    const recipeUrlInput = document.getElementById("recipe-url");
    const extractBtn = document.getElementById("extract-btn");
    const extractionLoader = document.getElementById("extraction-loader");
    const errorCard = document.getElementById("error-card");
    const errorMessage = document.getElementById("error-message");
    const recipeResults = document.getElementById("recipe-results");

    const historyTableBody = document.getElementById("history-table-body");
    const historyEmptyState = document.getElementById("history-empty-state");
    const refreshHistoryBtn = document.getElementById("refresh-history-btn");

    const mealPlannerActionBar = document.getElementById("meal-planner-action-bar");
    const selectedRecipesCount = document.getElementById("selected-recipes-count");
    const generatePlanBtn = document.getElementById("generate-plan-btn");
    const mealPlanSection = document.getElementById("meal-plan-section");
    const mealPlanLoader = document.getElementById("meal-plan-loader");
    const mealPlanResults = document.getElementById("meal-plan-results");
    const mealShoppingList = document.getElementById("meal-shopping-list");
    const mealPrepTips = document.getElementById("meal-prep-tips");

    const detailsModal = document.getElementById("details-modal");
    const modalContentArea = document.getElementById("modal-content-area");
    const closeModalBtn = document.getElementById("close-modal-btn");

    // ── Tab Navigation ──────────────────────────────────────────────────────
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const targetTab = tab.getAttribute("data-tab");
            tabs.forEach(t => t.classList.remove("active"));
            tabContents.forEach(tc => tc.classList.remove("active"));
            tab.classList.add("active");
            document.getElementById(`tab-${targetTab}`).classList.add("active");
            if (targetTab === "saved") {
                fetchHistory();
                resetMealPlannerState();
            }
        });
    });

    function resetMealPlannerState() {
        selectedRecipeIds = [];
        selectedRecipesCount.textContent = "0 recipes selected";
        generatePlanBtn.disabled = true;
        mealPlanSection.classList.add("hidden");
        mealPlanResults.classList.add("hidden");
        mealPlanLoader.classList.add("hidden");
    }

    // ── Safe JSON fetch helper (fixes the "not valid JSON" error) ───────────
    async function safeFetch(url, options = {}) {
        const response = await fetch(url, options);
        const contentType = response.headers.get("content-type") || "";
        let data;
        if (contentType.includes("application/json")) {
            data = await response.json();
        } else {
            // Server returned non-JSON (e.g. "Internal Server Error" HTML/text)
            const text = await response.text();
            throw new Error(text.slice(0, 200) || `Server error (${response.status})`);
        }
        if (!response.ok) {
            throw new Error(data.detail || data.message || `Request failed (${response.status})`);
        }
        return data;
    }

    // ── Extract Recipe ───────────────────────────────────────────────────────
    extractBtn.addEventListener("click", async () => {
        const url = recipeUrlInput.value.trim();
        if (!url) return;

        errorCard.classList.add("hidden");
        recipeResults.classList.add("hidden");
        extractionLoader.classList.remove("hidden");

        try {
            const result = await safeFetch(`${API_BASE}/api/extract`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url })
            });

            if (result.success && result.data) {
                renderRecipe(result.data, "res-");
                recipeResults.classList.remove("hidden");
            } else {
                throw new Error(result.message || "Extraction failed.");
            }
        } catch (err) {
            errorMessage.textContent = err.message;
            errorCard.classList.remove("hidden");
        } finally {
            extractionLoader.classList.add("hidden");
        }
    });

    // Allow pressing Enter in URL input
    recipeUrlInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") extractBtn.click();
    });

    // ── Render Recipe ────────────────────────────────────────────────────────
    function renderRecipe(recipe, prefix = "res-") {
        const heroEl = document.getElementById(`${prefix}hero`);
        if (heroEl) {
            heroEl.innerHTML = `
                <h2>${recipe.title}</h2>
                <div class="summary-meta-container">
                    <span class="summary-meta-item"><strong>Cuisine:</strong> ${recipe.cuisine || 'International'}</span>
                    <span class="summary-meta-item"><strong>Prep Time:</strong> ${recipe.prep_time || 'Not specified'}</span>
                    <span class="summary-meta-item"><strong>Cook Time:</strong> ${recipe.cook_time || 'Not specified'}</span>
                    <span class="summary-meta-item"><strong>Total Time:</strong> ${recipe.total_time || 'Not specified'}</span>
                    <span class="summary-meta-item"><strong>Servings:</strong> ${recipe.servings || 'Not specified'}</span>
                    <span class="summary-meta-item"><strong>Difficulty:</strong> ${recipe.difficulty || 'Medium'}</span>
                </div>
            `;
        }

        const ingListEl = document.getElementById(`${prefix}ingredients`);
        if (ingListEl) {
            ingListEl.innerHTML = "";
            if (recipe.ingredients && recipe.ingredients.length > 0) {
                recipe.ingredients.forEach(ing => {
                    const li = document.createElement("li");
                    li.innerHTML = `
                        <input type="checkbox" class="ing-chk">
                        <span class="ing-qty">${ing.quantity || ''} ${ing.unit || ''}</span>
                        <span>${ing.item}</span>
                    `;
                    const chk = li.querySelector(".ing-chk");
                    chk.addEventListener("change", () => li.classList.toggle("checked", chk.checked));
                    ingListEl.appendChild(li);
                });
            } else {
                ingListEl.innerHTML = "<p class='text-light'>No ingredients available.</p>";
            }
        }

        const instListEl = document.getElementById(`${prefix}instructions`);
        if (instListEl) {
            instListEl.innerHTML = "";
            if (recipe.instructions && recipe.instructions.length > 0) {
                recipe.instructions.forEach(step => {
                    const li = document.createElement("li");
                    li.textContent = step;
                    instListEl.appendChild(li);
                });
            } else {
                instListEl.innerHTML = "<p class='text-light'>No instructions available.</p>";
            }
        }

        const nutriEl = document.getElementById(`${prefix}nutrition`);
        if (nutriEl) {
            const n = recipe.nutrition || {};
            nutriEl.innerHTML = `
                <div class="nutrition-item"><strong>${n.calories || '—'}</strong><span>Calories</span></div>
                <div class="nutrition-item"><strong>${n.protein || '—'}</strong><span>Protein</span></div>
                <div class="nutrition-item"><strong>${n.carbs || '—'}</strong><span>Carbs</span></div>
                <div class="nutrition-item"><strong>${n.fat || '—'}</strong><span>Fat</span></div>
            `;
        }

        const subsEl = document.getElementById(`${prefix}substitutions`);
        if (subsEl) {
            subsEl.innerHTML = "";
            if (recipe.substitutions && recipe.substitutions.length > 0) {
                recipe.substitutions.forEach(sub => {
                    const li = document.createElement("li");
                    li.innerHTML = `
                        <div class="sub-title"><span>${sub.original}</span> &rarr; ${sub.substitute}</div>
                        <div class="sub-note">${sub.note}</div>
                    `;
                    subsEl.appendChild(li);
                });
            } else {
                subsEl.innerHTML = "<p class='text-light'>No substitutions suggested.</p>";
            }
        }

        const shopEl = document.getElementById(`${prefix}shopping-list`);
        if (shopEl) renderShoppingList(recipe.shopping_list, shopEl);

        const relatedEl = document.getElementById(`${prefix}related`);
        if (relatedEl) {
            relatedEl.innerHTML = "";
            if (recipe.related_recipes && recipe.related_recipes.length > 0) {
                recipe.related_recipes.forEach(rel => {
                    const div = document.createElement("div");
                    div.className = "related-item";
                    div.innerHTML = `<h4>${rel.title}</h4><p>${rel.description || ''} ${rel.estimated_time ? `(${rel.estimated_time})` : ''}</p>`;
                    relatedEl.appendChild(div);
                });
            } else {
                relatedEl.innerHTML = "<p class='text-light'>No related suggestions.</p>";
            }
        }
    }

    function renderShoppingList(list, targetElement) {
        targetElement.innerHTML = "";
        const categories = { dairy: "Dairy", produce: "Produce", pantry: "Pantry", meat: "Meat & Seafood", other: "Other" };
        let empty = true;
        Object.keys(categories).forEach(cat => {
            const items = list ? list[cat] : [];
            if (items && items.length > 0) {
                empty = false;
                const section = document.createElement("div");
                section.className = "shop-section";
                section.innerHTML = `
                    <div class="shop-title">${categories[cat]}</div>
                    <ul class="shop-ul">
                        ${items.map(item => `<li><input type="checkbox"> <span>${item}</span></li>`).join("")}
                    </ul>
                `;
                section.querySelectorAll("li").forEach(li => {
                    const chk = li.querySelector("input");
                    chk.addEventListener("change", () => {
                        li.querySelector("span").style.textDecoration = chk.checked ? "line-through" : "none";
                        li.querySelector("span").style.color = chk.checked ? "var(--text-light)" : "var(--text-medium)";
                    });
                });
                targetElement.appendChild(section);
            }
        });
        if (empty) targetElement.innerHTML = "<p class='text-light'>Shopping list is empty.</p>";
    }

    // ── History ──────────────────────────────────────────────────────────────
    async function fetchHistory() {
        try {
            const data = await safeFetch(`${API_BASE}/api/recipes`);
            savedRecipesList = data;
            renderHistoryTable(data);
            if (data && data.length > 0) {
                mealPlannerActionBar.classList.remove("hidden");
            } else {
                mealPlannerActionBar.classList.add("hidden");
            }
        } catch (err) {
            console.error("Error fetching recipe list:", err);
            historyTableBody.innerHTML = `<tr><td colspan="6" style="color:red;text-align:center;">Error loading recipes: ${err.message}</td></tr>`;
        }
    }

    function renderHistoryTable(recipes) {
        historyTableBody.innerHTML = "";
        if (!recipes || recipes.length === 0) {
            historyEmptyState.classList.remove("hidden");
            return;
        }
        historyEmptyState.classList.add("hidden");
        recipes.forEach(r => {
            const dateStr = new Date(r.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td class="select-col"><input type="checkbox" value="${r.id}" class="select-row-chk"></td>
                <td><strong>${r.title}</strong></td>
                <td>${r.cuisine || 'International'}</td>
                <td>${r.difficulty || 'Medium'}</td>
                <td>${dateStr}</td>
                <td class="actions-col">
                    <button class="btn-secondary" style="padding:6px 12px;font-size:13px;" data-id="${r.id}">Details</button>
                </td>
            `;
            const chk = tr.querySelector(".select-row-chk");
            chk.addEventListener("change", () => {
                if (chk.checked) selectedRecipeIds.push(r.id);
                else selectedRecipeIds = selectedRecipeIds.filter(id => id !== r.id);
                updateMealPlannerActionBar();
            });
            tr.querySelector("button").addEventListener("click", () => showRecipeDetailsModal(r.id));
            historyTableBody.appendChild(tr);
        });
    }

    refreshHistoryBtn.addEventListener("click", fetchHistory);

    function updateMealPlannerActionBar() {
        const count = selectedRecipeIds.length;
        selectedRecipesCount.textContent = `${count} recipe${count === 1 ? '' : 's'} selected`;
        generatePlanBtn.disabled = count < 2 || count > 5;
    }

    // ── Meal Planner ─────────────────────────────────────────────────────────
    generatePlanBtn.addEventListener("click", async () => {
        if (selectedRecipeIds.length < 2 || selectedRecipeIds.length > 5) return;
        mealPlanSection.classList.remove("hidden");
        mealPlanLoader.classList.remove("hidden");
        mealPlanResults.classList.add("hidden");

        try {
            const result = await safeFetch(`${API_BASE}/api/meal-plan`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ recipe_ids: selectedRecipeIds })
            });
            renderShoppingList(result.merged_shopping_list, mealShoppingList);
            mealPrepTips.innerHTML = "";
            if (result.meal_prep_tips && result.meal_prep_tips.length > 0) {
                result.meal_prep_tips.forEach(tip => {
                    const li = document.createElement("li");
                    li.innerHTML = `<i class="fa-solid fa-lightbulb"></i> <span>${tip}</span>`;
                    mealPrepTips.appendChild(li);
                });
            } else {
                mealPrepTips.innerHTML = "<li>No meal prep guidelines generated.</li>";
            }
            mealPlanResults.classList.remove("hidden");
        } catch (err) {
            alert("Meal Plan Generation Failed: " + err.message);
            mealPlanSection.classList.add("hidden");
        } finally {
            mealPlanLoader.classList.add("hidden");
        }
    });

    // ── Recipe Detail Modal ───────────────────────────────────────────────────
    async function showRecipeDetailsModal(id) {
        modalContentArea.innerHTML = `<div class="loader"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading...</div>`;
        detailsModal.classList.remove("hidden");
        try {
            const recipe = await safeFetch(`${API_BASE}/api/recipes/${id}`);
            modalContentArea.innerHTML = `
                <div class="recipe-card summary-card" id="modal-hero" style="margin-bottom:24px;margin-top:10px;"></div>
                <div class="details-grid">
                    <div class="grid-main">
                        <div class="recipe-card"><h3>Ingredients</h3><ul class="ingredients-list" id="modal-ingredients"></ul></div>
                        <div class="recipe-card"><h3>Instructions</h3><ol class="instructions-list" id="modal-instructions"></ol></div>
                    </div>
                    <div class="grid-side">
                        <div class="recipe-card"><h3>Nutrition Estimates (Per Serving)</h3><div class="nutrition-grid" id="modal-nutrition"></div></div>
                        <div class="recipe-card"><h3>Healthy Substitutions</h3><ul class="substitutions-list" id="modal-substitutions"></ul></div>
                        <div class="recipe-card"><h3>Shopping List</h3><div class="shopping-categories" id="modal-shopping-list"></div></div>
                        <div class="recipe-card"><h3>Related Recipes</h3><div class="related-list" id="modal-related"></div></div>
                    </div>
                </div>
            `;
            renderRecipe(recipe, "modal-");
        } catch (err) {
            modalContentArea.innerHTML = `<p style="color:var(--error-color);text-align:center;font-weight:600;">Error: ${err.message}</p>`;
        }
    }

    closeModalBtn.addEventListener("click", () => detailsModal.classList.add("hidden"));
    detailsModal.addEventListener("click", (e) => { if (e.target === detailsModal) detailsModal.classList.add("hidden"); });
});