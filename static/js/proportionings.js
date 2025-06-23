let fullData = [];
let currentPage = 1;
const rowsPerPage = 500;

// ---------------- UPDATE PROPORTIONING DATA ---------------- //
document.addEventListener("DOMContentLoaded", function () {
    fetchProportioningData("/api/proportionings");

    function addButtonEventListener(buttonId, callback) {
        const button = document.querySelector(buttonId);
        if (button) {
            button.addEventListener("click", callback);
        }
    }

    function showError(message) {
        const errorContainer = document.getElementById("error-container");
        if (errorContainer) {
            errorContainer.textContent = message;
            errorContainer.style.display = "block";
        }
    }

    async function loadArticleNames() {
        try {
            const response = await fetch('/api/articlenames');
            const articleNames = await response.json();
            const select = document.getElementById('RequestedArticle');

            select.length = 1;

            const fragment = document.createDocumentFragment();
            articleNames.forEach(article => {
                const option = document.createElement('option');
                option.value = article.ArticleName;
                option.textContent = article.ArticleName;
                fragment.appendChild(option);
            });
            select.appendChild(fragment);
        } catch (error) {
            console.error('Error loading article names:', error);
            showError('Failed to load article names. Please try again.');
        }
    }

    addButtonEventListener("#updateButton", () => {
        console.log("Update Table Data...");
        fetchProportioningData("/api/proportionings");
    });

    addButtonEventListener("#FilterButton", () => {
        console.log("Update Table (Filter) Data...");
        const switchChecked = document.querySelector("#ArticleFilterSwitch").checked;
        const requestedArticle = document.querySelector("#RequestedArticle").value;
        const ageSwitchChecked = document.querySelector("#AgeFilterSwitch").checked;
        const timeUnit = document.querySelector("#time-unit").value;
        const rangeValue = document.querySelector(".short-slider").value;

        const url = `/api/proportioningsfilter?switchChecked=${switchChecked}&requestedArticle=${requestedArticle}&ageSwitchChecked=${ageSwitchChecked}&timeUnit=${timeUnit}&rangeValue=${rangeValue}`;
        fetchProportioningData(url);
    });

    fetch("/common/PropId")
        .then(response => response.text())
        .then(data => {
            console.log("Fetched PropId:", data);
            const inputField = document.getElementById("PropIdInput");
            if (inputField) inputField.value = data;
        })
        .catch(error => {
            console.error("Error fetching current propDbId:", error);
            showError("Failed to fetch PropId. Please try again.");
        });

    loadArticleNames();
});

// ---------------- FETCH + PAGINATION ---------------- //
function fetchProportioningData(link) {
    console.time("RenderTableFetch");
    fetch(link)
        .then(response => response.json())
        .then(data => {
            fullData = data;
            currentPage = 1;
            renderTablePage(currentPage);
            renderPaginationControls();
            console.timeEnd("RenderTableFetch");
        })
        .catch(error => console.error("Error fetching data:", error));
}

function renderTablePage(page) {
    const tableBody = document.querySelector("#ProportioningTable tbody");
    tableBody.innerHTML = "";

    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const pageData = fullData.slice(start, end);

    const fragment = document.createDocumentFragment();

    pageData.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.ProportioningDBID}</td>
            <td>${row.ArticleDBID}</td>
            <td>${row.LotDBID}</td>
            <td>${row.VMSscan}</td>
            <td>${row.ArticleID}</td>
            <td>${row.ArticleName}</td>
            <td>${row.LotID}</td>
            <td>${row.Requested}</td>
            <td>${row.Actual}</td>
            <td>${row.Deviation}</td>
            <td>${row.Tolerance}</td>
            <td>${row.StartTime}</td>
            <td>${row.EndTime}</td>
            <td>${row.MixBoxID}</td>
            <td>${row.IngBoxID}</td>
            <td>${row.DosingLocation}</td>
            <td>${row.TypeOfDosing}</td>
            <td>${row.OrderID}</td>
        `;

        tr.addEventListener("click", function () {
            const propDbId = row.ProportioningDBID;
            console.log("Clicked row with PropDbId:", propDbId);

            fetch(`/api/rowclicked`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ propDbId })
            })
            .then(response => response.json())
            .then(result => {
                console.log("Backend response:", result);
                fetch("/common/PropId")
                    .then(response => response.text())
                    .then(data => {
                        const inputField = document.getElementById("PropIdInput");
                        if (inputField) inputField.value = data;
                    })
                    .catch(error => console.error("Error fetching current propDbId:", error));
            })
            .catch(error => console.error("Error sending data to backend:", error));
        });

        fragment.appendChild(tr);
    });

    tableBody.appendChild(fragment);
}

function renderPaginationControls() {
    const container = document.getElementById("pagination");
    container.innerHTML = "";

    const totalPages = Math.ceil(fullData.length / rowsPerPage);

    for (let i = 1; i <= totalPages; i++) {
        const btn = document.createElement("button");
        btn.textContent = i;
        btn.classList.add("pagination-button");
        if (i === currentPage) btn.classList.add("active");

        btn.addEventListener("click", () => {
            currentPage = i;
            renderTablePage(currentPage);
            renderPaginationControls();
        });

        container.appendChild(btn);
    }
}
